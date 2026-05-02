from pyrogram import Client, filters
from youtubesearchpython.__future__ import VideosSearch 
import os
import aiohttp
import requests
import random 
import asyncio
import yt_dlp 
from pyrogram.types import Chat, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from youtube_search import YoutubeSearch
import pytgcalls
from pytgcalls.types.input_stream.quality import (HighQualityAudio,
                                                  HighQualityVideo,
                                                  LowQualityAudio,
                                                  LowQualityVideo,
                                                  MediumQualityAudio,
                                                  MediumQualityVideo)
from typing import Union
from pyrogram import Client as client
from pyrogram.errors import (ChatAdminRequired,
                             UserAlreadyParticipant,
                             UserNotParticipant)
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import (AlreadyJoinedError,
                                  NoActiveGroupCall,
                                  TelegramServerError)
from pytgcalls.types import (JoinedGroupCallParticipant,
                             LeftGroupCallParticipant, Update)
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.stream import StreamAudioEnded
from config import PHOTO, LOGS
from Source.info import (db, add, is_served_call, add_active_video_chat, add_served_call, add_active_chat, gen_thumb, download, remove_active, joinch, active_progress_tasks)
from Source.Data import (get_logger, get_userbot, get_call, get_dev, get_dev_name, get_logger_mode, get_group, get_channel, get_bot_token)
import asyncio 
import time
from pyrogram.errors import PeerIdInvalid, MessageNotModified
from Source.progress import get_progress_bar



def panel_buttons(progress_bar="00:00 ──○────── 00:00"):
    return [
        [
            {"text": progress_bar, "callback_data": "none", "style": "primary"}
        ],
        [
            {"text": "▷", "callback_data": "resume", "style": "success"},
            {"text": "Ⅱ", "callback_data": "pause", "style": "primary"},
            {"text": "▷▷", "callback_data": "skip", "style": "success"},
            {"text": "■", "callback_data": "stop", "style": "danger"},
        ],
        [
            {"text": "↻ -10𝗌", "callback_data": "seek_back", "style": "success"},
            {"text": "⟳ +10𝗌", "callback_data": "seek_forward", "style": "danger"},
        ],
        [
            {"text": "⨁ Close", "callback_data": "close_panel", "style": "danger"}
        ]
    ]
@Client.on_callback_query(filters.regex("close_panel"))
async def close_panel(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
    except:
        pass

async def join_assistant(client, chat_id, message_id, userbot, file_path):
        join = None
        try:
            try:
                user = userbot.me
                user_id = user.id
                get = await client.get_chat_member(chat_id, user_id)
            except ChatAdminRequired:
                await client.send_message(chat_id, f"**≭︰ارفع البوت ادمن اولا**", reply_to_message_id=message_id)
            if get.status == ChatMemberStatus.BANNED:
                await client.send_message(chat_id, f"≭︰الغي الحظر عن المساعد لتتمكن من التشغيل\n≭︰الحساب المساعد ↫ ❲ @{user.username} ❳", reply_to_message_id=message_id)
            else:
              join = True
        except UserNotParticipant:
            chat = await client.get_chat(chat_id)
            if chat.username:
                try:
                    await userbot.join_chat(chat.username)
                    join = True
                except UserAlreadyParticipant:
                    join = True
                except Exception:
                 try:
                  invitelink = (await client.export_chat_invite_link(chat_id))
                  if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                  await asyncio.sleep(3)
                  await userbot.join_chat(invitelink)
                  join = True
                 except ChatAdminRequired:
                    return await client.send_message(chat_id, f"**≭︰اعطي البوت صلاحيه دعوه مستخدمين عبر الرابط**", reply_to_message_id=message_id)
                 except Exception as e:
                   await client.send_message(chat_id, f"**≭︰حدثت مشكله جرب مره اخرى او تواصل مع المطور**", reply_to_message_id=message_id)
            else:
                try:
                    try:
                       invitelink = chat.invite_link
                       if invitelink is None:
                          invitelink = (await client.export_chat_invite_link(chat_id))
                    except Exception:
                        try:
                          invitelink = (await client.export_chat_invite_link(chat_id))
                        except ChatAdminRequired:
                          await client.send_message(chat_id, f"**≭︰اعطي البوت صلاحيه دعوه مستخدمين عبر الرابط**", reply_to_message_id=message_id)
                        except Exception as e:
                          await client.send_message(chat_id, f"**≭︰حدثت مشكله جرب مره اخرى او تواصل مع المطور**", reply_to_message_id=message_id)
                    m = await client.send_message(chat_id, "**≭︰جاري تفعيل البوت**")
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace("https://t.me/+", "https://t.me/joinchat/")
                    await userbot.join_chat(invitelink)
                    join = True
                    await m.edit(f"≭︰انضم الحساب المساعد\n≭︰بدء تشغيل الموسيقى \n≭︰الحساب المساعد ↫❲[ {user.mention} ]❳")
                except UserAlreadyParticipant:
                    join = True
                except Exception as e:
                    await client.send_message(chat_id, f"**≭︰حدثت مشكله جرب مره اخرى او تواصل مع المطور**", reply_to_message_id=message_id)
        return join 
               
async def join_call(
        client,
        message_id,
        chat_id,
        bot_username,
        file_path,
        link,
        vid: Union[bool, str] = None):
    userbot = await get_userbot(bot_username)
    Done = None
    try:
        call = await get_call(bot_username)
    except Exception:
        return Done

    file_path = file_path
    audio_stream_quality = MediumQualityAudio()
    video_stream_quality = MediumQualityVideo()
    stream = (AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality) 
              if vid else AudioPiped(file_path, audio_parameters=audio_stream_quality))

    try:
        await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
        import time
        db[f"{bot_username}{chat_id}"][0]["start_time"] = time.time()
        Done = True
    except NoActiveGroupCall:
        h = await join_assistant(client, chat_id, message_id, userbot, file_path)
        if h:
            try:
                await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
                import time
                db[f"{bot_username}{chat_id}"][0]["start_time"] = time.time()
                Done = True
            except Exception:
                await client.send_message(chat_id, "**≭︰قم ببدأ مكالمه اولا**", reply_to_message_id=message_id)
    except AlreadyJoinedError:
        await call.leave_group_call(chat_id)
        try:
            await call.join_group_call(chat_id, stream, stream_type=StreamType().pulse_stream)
            import time
            db[f"{bot_username}{chat_id}"][0]["start_time"] = time.time()
            Done = True
        except Exception:
            await client.send_message(chat_id, "***≭︰اغلق الاتصال وقم بانشاء مكالمه جديده**", reply_to_message_id=message_id)
    except TelegramServerError:
        await client.send_message(chat_id, "**≭︰اغلق الاتصال وقم بانشاء مكالمه جديده**", reply_to_message_id=message_id)
    except Exception:
        return Done

    return Done

def seconds_to_min(seconds):
    if seconds is not None:
        seconds = int(seconds)
        d, h, m, s = (
            seconds // (3600 * 24),
            seconds // 3600 % 24,
            seconds % 3600 // 60,
            seconds % 3600 % 60,
        )
        if d > 0:
            return "{:02d}:{:02d}:{:02d}:{:02d}".format(d, h, m, s)
        elif h > 0:
            return "{:02d}:{:02d}:{:02d}".format(h, m, s)
        elif m > 0:
            return "{:02d}:{:02d}".format(m, s)
        elif s > 0:
            return "00:{:02d}".format(s)
    return "-"

async def logs(bot_username, client, message):
  try:
   if await get_logger_mode(bot_username) == "OFF":
     return
   logger = await get_logger(bot_username)
   log = LOGS
   if message.chat.type == ChatType.CHANNEL:
     chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
     name = f"{message.author_signature}" if message.author_signature else chat
     text = f"**≭︰بدأ تشغيل اغنيه ↯.\n\n≭︰اسم الكروب ↫ ❲ {chat} ❳\n≭︰ايدي الكروب ↫ ❲ {message.chat.id} ❳\n≭︰اسم المشغل : ↫❲ {name} ❳\n\n≭︰امر التشغيل ↫ ❲ {message.text} ❳**"
   else:
     chat = f"[{message.chat.title}](t.me/{message.chat.username})" if message.chat.username else message.chat.title
     user = f"≭︰معرف المشغل ↫ ❲ @{message.from_user.username} ❳" if message.from_user.username else f"≭︰ايدي المشغل ↫ ❲ {message.from_user.id} ❳"
     text = f"**≭︰بدأ تشغيل اغنيه **\n\n**≭︰اسم الكروب ↫ ❲ {chat} ❳**\n**≭︰ايدي الكروب ↫ ❲ {message.chat.id} ❳**\n**≭︰اسم المشغل ↫ ❲ {message.from_user.mention} ❳**\n**{user}**\n\n**≭︰امر التشغيل ↫ ❲ {message.text} ❳**"
   await client.send_message(logger, text=text, disable_web_page_preview=True)
   return await client.send_message(log, text=f"[ @{bot_username} ]\n{text}", disable_web_page_preview=True)
  except:
    pass

@Client.on_message(filters.command(["مين شغل", "م شغل", "مين مشغل"], ""))
async def last_played_user(client: Client, message):
    chat_id = message.chat.id
    bot_username = client.me.username

    last_user_id = db.get(f"{bot_username}_last_user_{chat_id}")
    if not last_user_id:
        return await message.reply_text("**≯︰لا يوجد أحد قام بالتشغيل حتى الآن .**")

    try:
        user = await client.get_users(last_user_id)
        name = user.first_name
        mention = f"[{name}](tg://user?id={last_user_id})"
        await message.reply_text(f"**≯︰آخر من قام بالتشغيل هو :** {mention}")
    except:
        await message.reply_text("**≯︰حدث خطأ في جلب معلومات آخر مشغل .**")

@Client.on_message(filters.command(["/play", "play", "/vplay", "شغل", "تشغيل", "فيد", "فيديو"], ""))
async def play(client: Client, message):
    if await joinch(message):
        return

    bot_username = client.me.username
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "odllll"
    message_id = message.id
    Source = message

    button = panel_buttons()

    try:
        await message.delete()
    except Exception:
        pass

    if message.chat.type == ChatType.PRIVATE:
        return await message.reply_text(
            "**≭︰لا يمكن تشغيلي هنا اضفني الى مجموعه**",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("اضف البوت لمجموعتك", url=f"https://t.me/{bot_username}?startgroup=True")]]
            )
        )

    rep = None
    if not len(message.command) == 1 or message.reply_to_message:
        try:
            rep = await message.reply_sticker("https://t.me/qsddddl/138")
        except Exception:
            pass

        try:
            call = await get_call(bot_username)
            await call.get_call(chat_id)
        except Exception:
            await remove_active(bot_username, chat_id)

        async def get_requester():
            if Source.views:
                return f"{message.author_signature}" if message.author_signature else message.chat.title
            return f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})"

        async def get_photo():
            default_url = "https://i.postimg.cc/GpRS4N9c/Picsart-25-11-01-04-33-34-146.jpg"
            try:
                if message.from_user and message.from_user.photo and message.from_user.photo.big_file_id:
                    return await client.download_media(message.from_user.photo.big_file_id)
                if message.chat.photo and message.chat.photo.big_file_id:
                    return await client.download_media(message.chat.photo.big_file_id)

                ahmed = await client.get_chat("cecrr")
                if ahmed.photo:
                    return await client.download_media(ahmed.photo.big_file_id)
            except Exception:
                pass
            return default_url

        async def send_reply(msg, photo, title, duration, requester, videoid, button, position=None, start=False):
            title = title[:18] if not start else title
            line1 = "Starting Playing Now" if start else f"Added Track To Playlist : {position if position is not None else '0'}"
            caption = (
                f"**⦿ {line1}**\n\n"
                f"◕ **Song Name:** {title[:18]}\n"
                f"◕ **Duration Time:** {duration}\n"
                f"◕ **Request By:** {requester}"
            )
            
            from Source.colored_api import send_colored_photo
            token = await get_bot_token(client.me.username)
            
            total_seconds = 0
            try:
                if ":" in duration:
                    parts = duration.split(":")
                    if len(parts) == 2:
                        total_seconds = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:
                        total_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            except:
                total_seconds = 0

            initial_bar = get_progress_bar(0, total_seconds)
            button_with_bar = panel_buttons(initial_bar)

            if token:
                response = await send_colored_photo(msg.chat.id, photo, caption, button_with_bar, token)
                message_id = response.get("result", {}).get("message_id") if isinstance(response, dict) else None
                
                try:
                    if message_id:
                        chat_db_key = f"{client.me.username}{msg.chat.id}"
                        if chat_db_key in db and len(db[chat_db_key]) > 0:
                            if start:
                                db[chat_db_key][0]["msg_id"] = message_id
                                
                                task_key = f"{client.me.username}{msg.chat.id}"
                                if task_key in active_progress_tasks:
                                    active_progress_tasks[task_key].cancel()
                                    
                                async def update_task():
                                    try:
                                        start_play_time = time.time()
                                        while True:
                                            await asyncio.sleep(8)
                                            if not await is_served_call(client, msg.chat.id):
                                                break
                                            
                                            current_song_data = db.get(chat_db_key, [{}])[0]
                                            if "pause_time" in current_song_data:
                                                continue
                                                
                                            current_pos = time.time() - current_song_data.get("start_time", start_play_time)
                                            new_bar = get_progress_bar(current_pos, total_seconds)
                                            new_buttons = panel_buttons(new_bar)
                                            from Source.colored_api import edit_colored_keyboard
                                            await edit_colored_keyboard(msg.chat.id, message_id, new_buttons, token)
                                    except asyncio.CancelledError:
                                        pass
                                    except:
                                        pass
                                
                                active_progress_tasks[task_key] = asyncio.create_task(update_task())
                            else:
                                db[chat_db_key][-1]["queue_msg_id"] = message_id
                except:
                    pass
            else:
                # في حال فشل جلب التوكن نستخدم الطريقة العادية
                res = await msg.reply_photo(photo=photo, caption=caption)
                if not start:
                    # حفظ الايدي في آخر أغنية أضيفت للقائمة
                    chat_db_key = f"{client.me.username}{msg.chat.id}"
                    if chat_db_key in db and len(db[chat_db_key]) > 0:
                        db[chat_db_key][-1]["queue_msg_id"] = res.id
            return True

        if not message.reply_to_message:
            name = None
            if len(message.command) == 1:
                if message.chat.type == ChatType.CHANNEL:
                    return await message.reply_text("**≯︰قم كتابة شيئ لتشغيلة .**")
                try:
                    name_msg = await client.ask(
                        chat_id,
                        text="**≯︰ارسل اسم او رابط الي تريد تشغيله .**",
                        reply_to_message_id=message_id,
                        filters=filters.user(user_id),
                        timeout=200
                    )
                    name = name_msg.text

                    if rep:
                        await rep.delete()
                    rep = await message.reply_sticker("https://t.me/qsddddl/138")
                except Exception:
                    return
            else:
                # استخراج اسم الأغنية بشكل صحيح بتجاهل كلمة الأمر فقط
                cmd_word = message.command[0]  # كلمة الأمر الأولى
                raw_text = message.text or ""
                # إزالة كلمة الأمر من بداية النص للحصول على اسم الأغنية
                if raw_text.startswith(cmd_word):
                    name = raw_text[len(cmd_word):].strip()
                else:
                    name = raw_text.split(None, 1)[1] if len(raw_text.split(None, 1)) > 1 else ""

            if not name:
                if rep:
                    return await rep.edit("**≯︰لم يتم إدخال اسم أغنية، يرجى كتابة اسم الأغنية بعد الأمر.**")
                return

            result = None
            try:
                results = VideosSearch(name, limit=1)
                response = await results.next()
                if response and response.get("result"):
                    result = response["result"][0]
            except Exception:
                pass

            # ✅ إذا فشل البحث الأساسي، جرب yt-dlp كاحتياطي
            if not result:
                try:
                    ydl_opts = {
                        "quiet": True,
                        "no_warnings": True,
                        "extract_flat": True,
                        "default_search": "ytsearch1",
                        "skip_download": True,
                    }
                    loop = asyncio.get_event_loop()
                    def _search():
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(f"ytsearch1:{name}", download=False)
                            if info and info.get("entries"):
                                e = info["entries"][0]
                                duration_s = e.get("duration", 0) or 0
                                mins = duration_s // 60
                                secs = duration_s % 60
                                return {
                                    "title": e.get("title", name),
                                    "duration": f"{mins:02d}:{secs:02d}",
                                    "id": e.get("id", ""),
                                    "link": f"https://www.youtube.com/watch?v={e.get('id', '')}",
                                }
                            return None
                    result = await loop.run_in_executor(None, _search)
                except Exception:
                    pass

            if not result:
                return await rep.edit(f"**≯︰لم يتم العثور على نتائج للبحث عن:** `{name}`")

            title = result["title"]
            duration = result["duration"]
            videoid = result["id"]
            yturl = result["link"]

            # كشف أوامر الفيديو بشكل دقيق بدون خلط مع كلمات أخرى
            _cmd = message.command[0].lower()
            vid = _cmd in ["/vplay", "vplay", "فيد", "فيديو"]

            try:
                if rep:
                    await rep.delete()
            except Exception:
                pass

            try:
                rep = await message.reply_sticker("https://t.me/qsddddl/138")
            except Exception:
                pass

            file_path = None

            if await is_served_call(client, chat_id):
                # ✅ أضف للقائمة أولاً (بدون ملف مؤقتاً)
                await add(chat_id, bot_username, None, yturl, title, duration, videoid, vid, user_id)

                if f"{bot_username}{chat_id}" in db:
                    db[f"{bot_username}_last_user_{chat_id}"] = user_id
                    position = len(db.get(f"{bot_username}{chat_id}")) - 1
                    requester = await get_requester()
                    photo = await gen_thumb(videoid, await get_photo(), bot_username, client)
                    await send_reply(message, photo, title, duration, requester, videoid, button, position)

                    # ✅ تحميل الملف في الخلفية مسبقاً حتى يكون جاهزاً عند التخطي
                    async def predownload_task(vid_id, is_video, b_username, c_id, idx):
                        try:
                            fp = await download(vid_id, is_video)
                            key = f"{b_username}{c_id}"
                            if fp and key in db and len(db[key]) > idx:
                                db[key][idx]["file_path"] = fp
                        except Exception:
                            pass
                    asyncio.create_task(predownload_task(videoid, vid, bot_username, chat_id, position))
            else:
                await add_active_chat(chat_id)
                await add_served_call(client, chat_id)
                if vid:
                    await add_active_video_chat(chat_id)

                # ✅ حذف الرسالة القديمة إن وجدت قبل البدء بجديد (فقط إذا كانت رسالة تشغيل)
                chat_db_key = f"{bot_username}{chat_id}"
                if chat_db_key in db and len(db[chat_db_key]) > 0:
                    old_msg_id = db[chat_db_key][0].get("msg_id")
                    if old_msg_id:
                        try:
                            await client.delete_messages(chat_id, old_msg_id)
                            db[chat_db_key][0]["msg_id"] = None # تنظيف الايدي
                        except:
                            pass

                file_path = await download(videoid, vid)
                if file_path is None:
                    await rep.edit("**≯︰حدث خطأ اثناء تحميل الفيديو.**")
                    return

                await add(chat_id, bot_username, file_path, yturl, title, duration, videoid, vid, user_id)
                db[f"{bot_username}_last_user_{chat_id}"] = user_id
                c = await join_call(client, message_id, chat_id, bot_username, file_path, yturl, vid)

                if not c:
                    await remove_active(bot_username, chat_id)
                    return await rep.delete()

                requester = await get_requester()
                photo = await gen_thumb(videoid, await get_photo(), bot_username, client)
                await send_reply(message, photo, title, duration, requester, videoid, button, start=True)

            await logs(bot_username, client, message)
            await rep.delete()

        else:
            media = (
                message.reply_to_message.audio or
                message.reply_to_message.voice or
                message.reply_to_message.video or
                message.reply_to_message.document
            )
            if not media:
                return await rep.edit("**≯︰الرد لا يحتوي على ملف صوتي أو فيديو صالح.**")

            file_path = await message.reply_to_message.download()
            vid = bool(message.reply_to_message.video or message.reply_to_message.document)
            title = getattr(media, "file_name", "ملف بدون اسم")
            duration = seconds_to_min(getattr(media, "duration", 0))
            link = None
            videoid = None
            photo = await get_photo()

            if await is_served_call(client, chat_id):
                await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
                db[f"{bot_username}_last_user_{chat_id}"] = user_id
                position = len(db.get(f"{bot_username}{chat_id}")) - 1
                requester = await get_requester()
                await send_reply(message, photo, title, duration, requester, videoid, button, position)
            else:
                await add_active_chat(chat_id)
                await add_served_call(client, chat_id)
                if vid:
                    await add_active_video_chat(chat_id)

                await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)
                db[f"{bot_username}_last_user_{chat_id}"] = user_id
                c = await join_call(client, message_id, chat_id, bot_username, file_path, link, vid)

                if not c:
                    await remove_active(bot_username, chat_id)
                    return await rep.delete()

                requester = await get_requester()
                await send_reply(message, photo, title, duration, requester, videoid, button, start=True)

            await logs(bot_username, client, message)
            await rep.delete()

    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass

    try:
        if photo and os.path.exists(photo) and photo.startswith("/"):
            os.remove(photo)
    except Exception:
        pass