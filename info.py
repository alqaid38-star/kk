import yt_dlp
import os
import time
import asyncio
import httpx
import concurrent.futures
import requests
from pathlib import Path
from typing import Union
from pyrogram import Client as app
from pyrogram import Client, filters
from pyrogram import Client as client
from yt_dlp import YoutubeDL
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import appp, OWNER, OWNER_NAME, infophoto, PHOTO
from pymongo import ASCENDING, DESCENDING
from Source.Data import (get_call, get_app, get_userbot, get_group, get_dev, get_dev_name, get_dev_id, get_data,
                         get_userbot, get_channel, must_join)
from config import API_ID, API_HASH, MONGO_DB_URL, user, call, logger, logger_mode, botname, helper as ass
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from youtubesearchpython.__future__ import VideosSearch
from pytgcalls import PyTgCalls, StreamType
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pytgcalls.types import (JoinedGroupCallParticipant,
                             LeftGroupCallParticipant, Update)
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.types.input_stream.quality import (HighQualityAudio,
                                                  HighQualityVideo,
                                                  LowQualityAudio,
                                                  LowQualityVideo,
                                                  MediumQualityAudio,
                                                  MediumQualityVideo)
import aiohttp
from io import BytesIO
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageFont
import textwrap
import re

API_URL = "http://82.112.241.247:5000"
executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

def get_ydl_opts(video=False, outtmpl=None):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
        'no_check_certificate': True,
        'concurrent_fragment_downloads': 5,
        'buffersize': 1024 * 1024 * 8,
        'retries': 5,
        'fragment_retries': 5,
    }
    if outtmpl:
        opts['outtmpl'] = outtmpl
    if video:
        opts['format'] = 'bestvideo+bestaudio/best'
        opts['merge_output_format'] = 'mp4'
    else:
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    return opts

async def download_from_api(video_id: str, video: bool = False):
    folder = "downloads"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ext = "mp4" if video else "mp3"
    file_path = os.path.join(folder, f"{video_id}.{ext}")
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        if video:
            response = requests.get(f"{API_URL}/download/video", params={"url": url}, stream=True, timeout=30)
        else:
            response = requests.get(f"{API_URL}/download/audio", params={"url": url}, stream=True, timeout=30)
        
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
                return file_path
    except Exception:
        pass
    
    return await download_with_ytdlp(video_id, video)

async def download_with_ytdlp(video_id: str, video: bool = False):
    folder = "downloads"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    ext = "mp4" if video else "mp3"
    file_path = os.path.join(folder, f"{video_id}.{ext}")
    
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return file_path
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    outtmpl = os.path.join(folder, f"{video_id}.%(ext)s")
    opts = get_ydl_opts(video=video, outtmpl=outtmpl)
    
    try:
        def run_download():
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])
        
        await asyncio.get_event_loop().run_in_executor(executor, run_download)
        
        if video:
            expected_file = os.path.join(folder, f"{video_id}.mp4")
            if not os.path.exists(expected_file):
                for f in os.listdir(folder):
                    if f.startswith(video_id) and f.endswith(('.mp4', '.mkv', '.webm')):
                        expected_file = os.path.join(folder, f)
                        break
            if os.path.exists(expected_file) and os.path.getsize(expected_file) > 10000:
                if not expected_file.endswith('.mp4'):
                    new_path = os.path.join(folder, f"{video_id}.mp4")
                    os.rename(expected_file, new_path)
                    expected_file = new_path
                return expected_file
        else:
            mp3_file = os.path.join(folder, f"{video_id}.mp3")
            if os.path.exists(mp3_file) and os.path.getsize(mp3_file) > 10000:
                return mp3_file
        return None
    except Exception:
        return None

async def download(video_id: str, video: bool = False):
    return await download_from_api(video_id, video)

async def get_video_info(video_id: str):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        resp = requests.get(f"{API_URL}/info", params={"url": url}, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('title'):
                duration = data.get('duration', 0)
                if duration:
                    minutes = duration // 60
                    seconds = duration % 60
                    duration_str = f"{minutes}:{seconds:02d}"
                else:
                    duration_str = "Unknown"
                return {
                    'title': data.get('title', 'Unknown Title'),
                    'duration': duration_str,
                    'views': data.get('views', 'Unknown'),
                    'channel': data.get('uploader', 'Unknown'),
                    'thumbnail': data.get('thumbnail', ''),
                    'video_id': video_id,
                }
    except Exception:
        pass
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = get_ydl_opts(video=False)
    try:
        def run_extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        
        info = await asyncio.get_event_loop().run_in_executor(executor, run_extract)
        if info is None:
            return None
        title = info.get('title', 'Unsupported Title')
        duration = info.get('duration', 0)
        if duration:
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "Unknown"
        views = info.get('view_count', 'Unknown Views')
        channel = info.get('channel', 'Unknown Channel')
        thumbnail = info.get('thumbnail', '')
        return {
            'title': title,
            'duration': duration_str,
            'views': views,
            'channel': channel,
            'thumbnail': thumbnail,
            'video_id': video_id,
        }
    except Exception:
        return None

def change_image_size(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

ouos = PHOTO

async def get_user_image(user_id, client):
    try:
        user = await client.get_users(user_id)
        if user.photo:
            image_file = await client.download_media(user.photo.big_file_id)
            return Image.open(image_file)
        else:
            return await get_user_image(6094238403, client)
    except Exception:
        async with aiohttp.ClientSession() as session:
            async with session.get(ouos) as response:
                if response.status == 200:
                    image_data = await response.read()
                    return Image.open(BytesIO(image_data))
                else:
                    return Image.new('RGB', (1280, 720), color=(255, 255, 255))

async def gen_thumb(videoid, photo, bot_username, client):
    downloads_path = Path("./downloads")
    downloads_path.mkdir(parents=True, exist_ok=True)
    output_file = downloads_path / f"{photo}.png"

    if output_file.is_file():  
        return str(output_file)  

    try:  
        userbot = await get_userbot(bot_username)  
        mongodb = await get_data(client)  
        dev_id = await get_dev_id(bot_username)  
        dev_image = await get_user_image(dev_id, client)  

        if dev_image is None:  
            dev_image = await get_user_image(6094238403, client)  

        url = f"https://www.youtube.com/watch?v={videoid}"  
        results = VideosSearch(url, limit=1)  
        
        search_results = (await results.next()).get("result")
        if not search_results:
            return ouos
            
        result = search_results[0]
        
        try:  
            title = result["title"]  
            title = re.sub("\W+", " ", title)  
            title = title.title()  
        except:  
            title = "Unsupported Title"  
        try:  
            duration = result["duration"]  
        except:  
            duration = "Unknown Mins"  
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]  
        try:  
            views = result["viewCount"]["short"]  
        except:  
            views = "Unknown Views"  
        try:  
            channel = result["channel"]["name"]  
        except:  
            channel = "Unknown Channel"  

        async with aiohttp.ClientSession() as session:  
            async with session.get(thumbnail) as resp:  
                if resp.status == 200:  
                    image_data = await resp.read()  
                    thumbnail_image = Image.open(BytesIO(image_data))  
                else:  
                    return ouos  

        youtube_image = thumbnail_image  
        youtube_image = change_image_size(1280, 720, youtube_image)  

        background = youtube_image.filter(ImageFilter.BoxBlur(5))  
        enhancer = ImageEnhance.Brightness(background)  
        background = enhancer.enhance(0.6)  
        Xcenter = dev_image.width / 2  
        Ycenter = dev_image.height / 2  
        x1 = Xcenter - 250  
        y1 = Ycenter - 250  
        x2 = Xcenter + 250  
        y2 = Ycenter + 250  
        logo = dev_image.crop((x1, y1, x2, y2))  
        logo.thumbnail((520, 520), Image.Resampling.LANCZOS)  
        logo = ImageOps.expand(logo, border=15, fill="white")  
        background.paste(logo, (50, 100))  

        draw = ImageDraw.Draw(background)  
        font = ImageFont.truetype("./alqaid/font2.ttf", 40)  
        font2 = ImageFont.truetype("./alqaid/font2.ttf", 70)  
        arial = ImageFont.truetype("./alqaid/font2.ttf", 30)  
        para = textwrap.wrap(title, width=32)  
        j = 0  
        draw.text(  
            (600, 150),  
            infophoto,  
            fill="white",  
            stroke_width=2,  
            stroke_fill="white",  
            font=font2,  
        )  
        for line in para:  
            if j == 1:  
                j += 1  
                draw.text(  
                    (600, 340),  
                    f"{line}",  
                    fill="white",  
                    stroke_width=1,  
                    stroke_fill="white",  
                    font=font,  
                )  
            if j == 0:  
                j += 1  
                draw.text(  
                    (600, 280),  
                    f"{line}",  
                    fill="white",  
                    stroke_width=1,  
                    stroke_fill="white",  
                    font=font,  
                )  

        views = str(views)  
        duration = str(duration)  
        channel = str(channel)  

        draw.text(  
            (600, 450),  
            f"Views : {views[:23]}",  
            (255, 255, 255),  
            font=arial,  
        )  
        draw.text(  
            (600, 500),  
            f"Duration : {duration[:23]} Mins",  
            (255, 255, 255),  
            font=arial,  
        )  
        draw.text(  
            (600, 550),  
            f"Channel : {channel}",  
            (255, 255, 255),  
            font=arial,  
        )  

        background.save(output_file)  
        return str(output_file)  
    except Exception:  
        return ouos
    
db = {}

async def add(
        chat_id,
        bot_username,
        file_path,
        link,
        title,
        duration,
        videoid,
        vid,
        user_id):
    put = {
        "title": title,
        "dur": duration,
        "user_id": user_id,
        "chat_id": chat_id,
        "vid": vid,
        "file_path": file_path,
        "link": link,
        "videoid": videoid,
        "played": 0,
    }
    chat_id = f"{bot_username}{chat_id}"
    i = db.get(chat_id)
    if not i:
        db[chat_id] = []
    db[chat_id].append(put)
    return

async def is_served_user(client, user_id: int) -> bool:
    userdb = await get_data(client)
    userdb = userdb.users
    user = await userdb.find_one({"user_id": user_id})
    return bool(user)

async def get_served_users(client) -> list:
    userdb = await get_data(client)
    userdb = userdb.users
    users_list = []
    async for user in userdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list

async def add_served_user(client, user_id: int):
    userdb = await get_data(client)
    userdb = userdb.users
    if await is_served_user(client, user_id):
        return
    return await userdb.insert_one({"user_id": user_id})

async def del_served_user(client, user_id: int):
    chats = await get_data(client)
    chatsdb = chats.users
    if not await is_served_user(client, user_id):
        return
    return await chatsdb.delete_one({"user_id": user_id})

async def get_served_chats(client) -> list:
    chats = await get_data(client)
    chatsdb = chats.chats
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list

async def is_served_chat(client, chat_id: int) -> bool:
    chats = await get_data(client)
    chatsdb = chats.chats
    chat = await chatsdb.find_one({"chat_id": chat_id})
    return bool(chat)

async def add_served_chat(client, chat_id: int):
    chats = await get_data(client)
    chatsdb = chats.chats
    if await is_served_chat(client, chat_id):
        return
    return await chatsdb.insert_one({"chat_id": chat_id})

async def del_served_chat(client, chat_id: int):
    chats = await get_data(client)
    chatsdb = chats.chats
    if not await is_served_chat(client, chat_id):
        return
    return await chatsdb.delete_one({"chat_id": chat_id})

activecall = {}

async def get_served_call(bot_username) -> list:
    return activecall[bot_username]

async def is_served_call(client, chat_id: int) -> bool:
    bot_username = client.me.username
    if chat_id not in activecall.get(bot_username, []):
        return False
    else:
        return True

async def add_served_call(client, chat_id: int):
    bot_username = client.me.username
    if chat_id not in activecall.setdefault(bot_username, []):
        activecall[bot_username].append(chat_id)

async def remove_served_call(bot_username, chat_id: int):
    if chat_id in activecall.get(bot_username, []):
        activecall[bot_username].remove(chat_id)

active = []

async def get_active_chats() -> list:
    return active

async def is_active_chat(chat_id: int) -> bool:
    if chat_id not in active:
        return False
    else:
        return True

async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)

async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)

activevideo = []

async def get_active_video_chats() -> list:
    return activevideo

async def is_active_video_chat(chat_id: int) -> bool:
    if chat_id not in activevideo:
        return False
    else:
        return True

async def add_active_video_chat(chat_id: int):
    if chat_id not in activevideo:
        activevideo.append(chat_id)

async def remove_active_video_chat(chat_id: int):
    if chat_id in activevideo:
        activevideo.remove(chat_id)

async def remove_active(bot_username, chat_id: int):
    chat = f"{bot_username}{chat_id}"
    try:
        if chat in db and len(db[chat]) > 0:
            msg_id = db[chat][0].get("msg_id")
            if msg_id:
                try:
                    app_ = appp.get(bot_username)
                    if app_:
                        await app_.delete_messages(chat_id, msg_id)
                except:
                    pass

        db[chat] = []
        del db[chat]
    except:
        pass
    try:
        await remove_active_video_chat(chat_id)
    except:
        pass
    try:
        await remove_active_chat(chat_id)
    except:
        pass
    try:
        await remove_served_call(bot_username, chat_id)
    except:
        pass

active_progress_tasks = {}

async def change_stream(bot_username, client, chat_id):
    chat = f"{bot_username}{chat_id}"
    app = appp.get(bot_username)

    if not app:
        return

    try:
        check = db.get(chat)
        if not check or len(check) <= 1:
            if check and len(check) > 0:
                old_msg_id = check[0].get("msg_id")
                if old_msg_id:
                    try:
                        await app.delete_messages(chat_id, old_msg_id)
                    except:
                        pass

            await remove_active(bot_username, chat_id)
            try:
                return await client.leave_group_call(chat_id)
            except Exception:
                return

        try:
            old_msg_id = check[0].get("msg_id")
            if old_msg_id:
                try:
                    await app.delete_messages(chat_id, old_msg_id)
                except:
                    pass
            
            check.pop(0)
            data = check[0]

            queue_msg_id = data.get("queue_msg_id")
            if queue_msg_id:
                try:
                    await app.delete_messages(chat_id, queue_msg_id)
                except:
                    pass
        except Exception:
            await remove_active(bot_username, chat_id)
            return await client.leave_group_call(chat_id)

        file_path = data.get("file_path")
        title = data.get("title", "Unknown Title")
        dur = data.get("dur", "Unknown Duration")
        user_id = data.get("user_id")
        video = data.get("vid")
        videoid = data.get("videoid")
        link = f"https://www.youtube.com/watch?v={videoid}" if videoid and videoid != "None" else None
        check[0]["played"] = 0

        audio_stream_quality = MediumQualityAudio()
        video_stream_quality = MediumQualityVideo()

        if videoid and videoid != "None" and (not file_path or not os.path.exists(str(file_path))):
            try:
                file_path = await download(videoid, video)
                if file_path:
                    data["file_path"] = file_path
                else:
                    try:
                        await app.send_message(chat_id, f"**≯︰حدث خطأ أثناء تحميل الأغنية التاليه، سيتم التخطي.**")
                    except:
                        pass
                    return await change_stream(bot_username, client, chat_id)
            except Exception:
                try:
                    await app.send_message(chat_id, f"**≯︰حدث خطأ أثناء تحميل الأغنية التاليه، سيتم التخطي.**")
                except:
                    pass
                return await change_stream(bot_username, client, chat_id)

        if not file_path or not os.path.exists(str(file_path)):
            try:
                await app.send_message(chat_id, f"**≯︰الملف غير موجود، سيتم تخطي الأغنية.**")
            except:
                pass
            return await change_stream(bot_username, client, chat_id)

        stream = AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) if video else AudioPiped(file_path, audio_parameters=audio_stream_quality)

        try:
            await client.change_stream(chat_id, stream)
            import time
            db[chat][0]["start_time"] = time.time()
        except Exception as e:
            try:
                await app.send_message(chat_id, f"**≯︰حدثت مشكلة أثناء تغيير التشغيل: {e}**")
            except:
                pass
            return await change_stream(bot_username, client, chat_id)

        try:
            photo_path = PHOTO
            if videoid:
                try:
                    user = await app.get_users(user_id)
                    if user.photo:
                        u_photo = await app.download_media(user.photo.big_file_id)
                        photo_path = await gen_thumb(videoid, u_photo, bot_username, app)
                    else:
                        photo_path = await gen_thumb(videoid, PHOTO, bot_username, app)
                except:
                    photo_path = await gen_thumb(videoid, PHOTO, bot_username, app)
            
            img = photo_path if photo_path and os.path.exists(photo_path) else PHOTO
        except Exception:
            img = PHOTO

        try:
            chat_info = await app.get_chat(chat_id)
            requester = f"[{chat_info.title}](https://t.me/{chat_info.username})" if chat_info.username else chat_info.title or f"Chat {chat_id}"
        except Exception:
            requester = f"Chat {chat_id}"

        from Source.play import panel_buttons
        from Source.Data import get_bot_token
        
        token = await get_bot_token(bot_username)
        
        total_seconds = 0
        try:
            if ":" in dur:
                parts = dur.split(":")
                if len(parts) == 2:
                    total_seconds = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        except:
            total_seconds = 0
            
        from Source.progress import get_progress_bar
        initial_bar = get_progress_bar(0, total_seconds)
        button = panel_buttons(initial_bar)
        caption = f"**⦿ Starting Playing Now\n\n◕ Song Name: {title[:18]}\n◕ Duration: {dur}\n◕ Requested By: {requester}**"

        if token:
            from Source.colored_api import send_colored_photo, edit_colored_keyboard
            response = await send_colored_photo(chat_id, img, caption, button, token)
            message_id = response.get("result", {}).get("message_id") if isinstance(response, dict) else None
            
            if message_id:
                db[chat][0]["msg_id"] = message_id
                
                task_key = f"{bot_username}{chat_id}"
                if task_key in active_progress_tasks:
                    active_progress_tasks[task_key].cancel()
                
                async def update_task():
                    try:
                        start_play_time = time.time()
                        while True:
                            await asyncio.sleep(8)
                            if not await is_served_call(app, chat_id):
                                break
                            
                            current_song_data = db.get(chat, [{}])[0]
                            if "pause_time" in current_song_data:
                                continue
                            
                            current_pos = time.time() - current_song_data.get("start_time", start_play_time)
                            new_bar = get_progress_bar(current_pos, total_seconds)
                            new_buttons = panel_buttons(new_bar)
                            await edit_colored_keyboard(chat_id, message_id, new_buttons, token)
                    except:
                        pass
                
                active_progress_tasks[task_key] = asyncio.create_task(update_task())
        else:
            from pyrogram.types import InlineKeyboardMarkup
            await app.send_photo(chat_id, photo=img, caption=caption, reply_markup=InlineKeyboardMarkup(button))

    except Exception:
        pass

async def helper(bot_username):
    user = await get_userbot(bot_username)

    @user.on_message(filters.private)
    async def helperuser(client, update):
        if not update.chat.id in ass[bot_username]:
            ass[bot_username].append(update.chat.id)

async def Call(bot_username):
    call = await get_call(bot_username)

    @call.on_kicked()
    @call.on_closed_voice_chat()
    @call.on_left()
    async def stream_services_handler(client, chat_id: int):
        return await remove_active(bot_username, chat_id)

    @call.on_stream_end()
    async def stream_end_handler1(client, update: Update):
        if not isinstance(update, StreamAudioEnded):
            return
        await change_stream(bot_username, client, update.chat_id)

async def joinch(message):
    try:
        if not message.from_user:
            return

        ii = await must_join(message._client.me.username)
        if ii == "معطل":
            return

        cch = await get_channel(message._client.me.username)
        ch = cch.replace("https://t.me/", "") if cch.startswith("https://t.me/") else cch

        try:
            await message._client.get_chat_member(ch, message.from_user.id)
        except UserNotParticipant:
            try:
                await message.reply(
                    f"**🚦 يجب ان تشترك في القناة\n\nقنـاة الـبـوت : « {cch} »**",
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("اضـغط هنا للأشتـراك القنـاة 🚦", url=f"https://t.me/{ch}")]]
                    )
                )
            except ChatAdminRequired:
                pass
            return True
        except ChatAdminRequired:
            pass
        except:
            pass

    except:
        pass