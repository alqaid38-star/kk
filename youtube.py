import re
import os
import httpx
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType
from youtube_search import YoutubeSearch

API_BASE = "http://82.112.241.247:5000"
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

class VideoDownloader:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(10)
        self.api_base = API_BASE
    
    def extract_video_id(self, url: str) -> str:
        if "youtu.be" in url:
            return url.split("/")[-1].split("?")[0]
        if "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        return url
    
    async def get_info(self, video_url: str):
        async with self.semaphore:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        f"{self.api_base}/info",
                        params={"url": video_url}
                    )
                    if response.status_code == 200:
                        return response.json()
                    return None
            except Exception:
                return None
    
    async def download(self, video_id: str, video: bool = False):
        async with self.semaphore:
            ext = "mp4" if video else "mp3"
            file_path = os.path.join(DOWNLOAD_FOLDER, f"{video_id}.{ext}")
            
            if os.path.exists(file_path) and os.path.getsize(file_path) > 5000:
                return file_path
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            endpoint = f"{self.api_base}/download/video" if video else f"{self.api_base}/download/audio"
            
            try:
                async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    response = await client.get(endpoint, params={"url": video_url}, headers=headers)
                    
                    if response.status_code == 200 and len(response.content) > 5000:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        return file_path
                    return None
            except Exception:
                return None

downloader = VideoDownloader()

@Client.on_message(filters.command(["/song", "/video", "نزل", "تنزيل", "حمل", "تحميل", "يوت", "بحث"], "") & (filters.group | filters.channel | filters.private))
async def downloaded(client: Client, message: Message):
    video_commands = ["/video", "حمل", "تحميل"]
    
    if len(message.command) == 1:
        if message.chat.type == ChatType.PRIVATE:
            ask = await client.ask(message.chat.id, "**≭︰ارسل اسم المقطع الآن**")
            query = ask.text
            m = await ask.reply_text("**≭︰جاري البحث والتحميل... ⚡**")
        else:
            try:
                ask = await client.ask(
                    message.chat.id,
                    "**≭︰ارسل الاسم الآن**",
                    filters=filters.user(message.from_user.id),
                    reply_to_message_id=message.id,
                    timeout=15
                )
                query = ask.text
                m = await ask.reply_text("**≭︰جاري البحث والتحميل... ⚡**")
            except:
                return
    else:
        query = message.text.split(None, 1)[1]
        m = await message.reply_text("**≭︰جاري البحث والتحميل... ⚡**")
    
    is_video = message.command[0] in video_commands
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        
        if not results:
            await m.edit("**❌ لم يتم العثور على نتائج.**")
            return
        
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        
        video_id = downloader.extract_video_id(link)
        
        if not video_id:
            await m.edit("**❌ خطأ في رابط الفيديو.**")
            return
        
        file_path = await downloader.download(video_id, is_video)
        
        if not file_path or not os.path.exists(file_path):
            await m.edit("**❌ فشل التحميل من السيرفر.**")
            return
        
        if is_video:
            await message.reply_video(
                file_path, 
                caption=title[:200], 
                supports_streaming=True
            )
        else:
            await message.reply_audio(
                file_path, 
                caption=f"**• Uploader: @{client.me.username}**", 
                title=title[:200]
            )
        
        try:
            os.remove(file_path)
        except:
            pass
        
        await m.delete()
        
    except Exception:
        await m.edit("**❌ حدث خطأ، حاول مرة أخرى.**")