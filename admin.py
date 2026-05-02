import asyncio
from config import OWNER, OWNER_NAME, PHOTO
from pyrogram import Client, filters
from Source.info import (remove_active, is_served_call, joinch)
from Source.Data import (get_call, get_dev, get_dev_name, get_group, get_channel)
from Source.info import (add, db, download, gen_thumb, change_stream)
from pytgcalls import PyTgCalls, StreamType
from pyrogram.enums import ChatType, ChatMemberStatus
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (HighQualityAudio,
                                                  HighQualityVideo,
                                                  LowQualityAudio,
                                                  LowQualityVideo,
                                                  MediumQualityAudio,
                                                  MediumQualityVideo)

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import CallbackQuery
import os
from Source.play import panel_buttons

# ========== CALLBACK QUERY HANDLER ==========
@Client.on_callback_query(
    filters.regex(pattern=r"^(pause|skip|stop|resume|seek_back|seek_forward)$")
)
async def admin_risghts_callback(client: Client, callback_query: CallbackQuery):
    try:
        bot_username = client.me.username
        dev = await get_dev(bot_username)
        chat_member = await client.get_chat_member(callback_query.message.chat.id, callback_query.from_user.id)
        if not chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            if callback_query.from_user.id != dev:
                if callback_query.from_user.username not in OWNER:
                    await callback_query.answer("≭︰انت لست مشرف", show_alert=True)
                    return

        command = callback_query.matches[0].group(1)
        chat_id = callback_query.message.chat.id
        if not await is_served_call(client, chat_id):
            await callback_query.answer("≭︰لم تقم بتشغيل شي", show_alert=True)
            return

        call = await get_call(bot_username)

        if command == "pause":
            await call.pause_stream(chat_id)
            import time
            chat = f"{bot_username}{chat_id}"
            if chat in db and len(db[chat]) > 0:
                db[chat][0]["pause_time"] = time.time()
            await callback_query.answer("≭︰تم ايقاف التشغيل موقتا", show_alert=True)
            await callback_query.message.reply_text(f"{callback_query.from_user.mention} **≭︰تم ايقاف التشغيل بواسطه ↫**")

        elif command == "resume":
            await call.resume_stream(chat_id)
            import time
            chat = f"{bot_username}{chat_id}"
            if chat in db and len(db[chat]) > 0:
                data = db[chat][0]
                if "pause_time" in data:
                    pause_duration = time.time() - data["pause_time"]
                    data["start_time"] = data.get("start_time", time.time()) + pause_duration
                    data.pop("pause_time")
            await callback_query.answer("≭︰تم استئناف التشغيل", show_alert=True)
            await callback_query.message.reply_text(f"{callback_query.from_user.mention} **≭︰تم استئناف التشغيل بواسطه ↫**")

        elif command == "stop":
            try:
                await call.leave_group_call(chat_id)
            except Exception:
                pass
            await remove_active(bot_username, chat_id)
            await callback_query.answer("≭︰تم ايقاف التشغيل ", show_alert=True)
            await callback_query.message.reply_text(f"{callback_query.from_user.mention} **≭︰تم انهاء التشغيل بواسطه ↫**")

        elif command in ["seek_forward", "seek_back"]:
            import time, datetime
            chat = f"{bot_username}{chat_id}"
            if chat not in db or len(db[chat]) == 0:
                await callback_query.answer("≭︰لا يوجد شيء لتغيير وقته", show_alert=True)
                return
            
            data = db[chat][0]
            file_path = data.get("file_path")
            
            # محاولة التحقق من الملف وإعادة تحميله إذا لزم الأمر
            if not file_path or not os.path.exists(file_path):
                videoid = data.get("videoid")
                vid = data.get("vid", False)
                if videoid:
                    await callback_query.answer("≭︰جاري مزامنة الملف...", show_alert=False)
                    from Source.info import download
                    file_path = await download(videoid, vid)
                    data["file_path"] = file_path
                
            if not file_path or not os.path.exists(file_path):
                await callback_query.answer("≭︰الملف غير متوفر حالياً على الخادم", show_alert=True)
                return

            now = time.time()
            start_time = data.get("start_time", now)
            pause_time = data.get("pause_time")
            
            if pause_time:
                current_pos = pause_time - start_time
            else:
                current_pos = now - start_time
            
            if command == "seek_forward":
                new_pos = current_pos + 10
            else:
                new_pos = max(0, current_pos - 10)
            
            video = data.get("vid", False)
            audio_stream_quality = MediumQualityAudio()
            video_stream_quality = MediumQualityVideo()
            seek_str = str(datetime.timedelta(seconds=int(new_pos)))
            
            stream = (AudioVideoPiped(file_path, audio_parameters=audio_stream_quality, video_parameters=video_stream_quality, additional_ffmpeg_parameters=f"-ss {seek_str}") 
                      if video else AudioPiped(file_path, audio_parameters=audio_stream_quality, additional_ffmpeg_parameters=f"-ss {seek_str}"))
            
            try:
                await call.change_stream(chat_id, stream)
                data["start_time"] = time.time() - new_pos
                if pause_time:
                    data.pop("pause_time")
                await callback_query.answer(f"≭︰تم الانتقال إلى {seek_str}", show_alert=False)
            except Exception as e:
                await callback_query.answer(f"≭︰خطأ: {e}", show_alert=True)

        elif command == "skip":
            await callback_query.answer("≭︰جاري التخطي...", show_alert=False)
            from Source.info import change_stream
            await change_stream(bot_username, call, chat_id)

    except Exception:
        pass


# ========== MESSAGE HANDLER ==========
@Client.on_message(filters.command(["/stop", "/end", "/skip", "/resume", "/pause", "/loop", "ايقاف مؤقت", "استكمال", "تخطي", "انهاء", "اسكت", "ايقاف", "تكرار", "كررها"], "") & ~filters.private)
async def admin_rights_message(client: Client, message):
    try:
        if await joinch(message):
            return
        bot_username = client.me.username
        dev = await get_dev(bot_username)

        if message.chat.type != ChatType.CHANNEL:
            chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if not chat_member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                if message.from_user.id != dev:
                    if message.from_user.username not in OWNER:
                        await message.reply_text("**≭︰انت لست مشرف**")
                        return

        command = message.command[0]
        chat_id = message.chat.id

        if not await is_served_call(client, chat_id):
            await message.reply_text("**≭︰لا يوجد شئ في قائمه التشغيل**")
            return

        call = await get_call(bot_username)

        if command in ["/pause", "ايقاف مؤقت"]:
            await call.pause_stream(chat_id)
            await message.reply_text(f"**≭︰تم ايقاف التشغيل مؤقتا**")

        elif command in ["/resume", "استكمال", "استئناف"]:
            await call.resume_stream(chat_id)
            await message.reply_text(f"**≭︰تم استئناف التشغيل**")

        elif command in ["/stop", "/end", "اسكت", "انهاء", "ايقاف"]:
            try:
                await call.leave_group_call(chat_id)
            except Exception:
                pass
            await remove_active(bot_username, chat_id)
            await message.reply_text(f"**≭︰تم انهاء التشغيل**")

        elif command in ["تكرار", "كررها", "/loop"]:
            if len(message.text.split()) == 1:
                await message.reply_text("**≭︰قم بتحديد عدد مرات التكرار**")
                return
            x = message.text.split(None, 1)[1]
            if x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
                repeat_count = int(x)
                repeat_text = f"{repeat_count} مره" if repeat_count == 1 else f"{repeat_count} مرات"
            elif x == "مره":
                repeat_count = 1
                repeat_text = "مره واحده"
            elif x == "مرتين":
                repeat_count = 2
                repeat_text = "مرتين"
            else:
                await message.reply_text("**≭︰استخدام خطا**\n**≭︰طريقه الاستخدام ↫❲ تكرار 4 ❳**")
                return

            chat = f"{bot_username}{chat_id}"
            check = db.get(chat)
            if not check or len(check) == 0:
                await message.reply_text("لا توجد أغنية حالية للتكرار")
                return

            first = check[0]
            file_path = first.get("file_path")
            title = first.get("title")
            duration = first.get("dur")
            user_id = first.get("user_id")
            vid = first.get("vid")
            link = first.get("link")
            videoid = first.get("videoid")

            for _ in range(repeat_count):
                await add(chat_id, bot_username, file_path, link, title, duration, videoid, vid, user_id)

            await message.reply_text(f"**≭︰تم تحديد التكرار {repeat_text}**")

        elif command in ["/skip", "تخطي"]:
            from Source.info import change_stream
            await change_stream(bot_username, call, chat_id)

        else:
            await message.reply_text("**≭︰استخدام خطا  .. **")

    except Exception:
        pass