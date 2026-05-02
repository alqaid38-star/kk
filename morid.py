import random
import logging
import asyncio
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ParseMode, ChatMembersFilter
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges, Message, ChatMemberUpdated
from pyrogram.errors import FloodWait
from Source.Data import get_dev

logger = logging.getLogger(__name__)

# ======================== البيانات الأساسية ========================
devchannel = {}  
source = "https://t.me/source_Asyuti"  
id_enabled = []
wenru = []
caes = []

welcome_enabled = True
promotion_lock = []
locks = {"promotion_lock": []}
user_waiting = {}
temp_storage = {}
admin_edit_cache = {}

LOCK_FILE = "locks_data.json"

def load_locks():
    global promotion_lock, locks
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r") as f:
                data = json.load(f)
                promotion_lock = data.get("promotion_lock", [])
                locks["promotion_lock"] = promotion_lock
        except:
            pass

def save_locks(locks_data):
    with open(LOCK_FILE, "w") as f:
        json.dump({"promotion_lock": locks_data.get("promotion_lock", [])}, f)

load_locks()

# ======================== دوال مساعدة ========================
async def johned(client, message):
    return False

async def checkg_member_status(user_id, message, client):
    return True

def perm_map(perm):
    mapping = {
        "del": "delete_messages",
        "ban": "restrict_members",
        "pin": "pin_messages",
        "call": "manage_video_chats",
        "invite": "invite_users",
        "info": "change_info",
        "promo": "promote_members"
    }
    return mapping.get(perm, "")

async def zom_ask(client: Client, message: Message, text: str, timeout: int = 30):
    sender_id = message.from_user.id if message.from_user else message.sender_chat.id
    chat_id = message.chat.id
    await client.send_message(chat_id, text)
    future = asyncio.get_event_loop().create_future()
    user_waiting[sender_id] = future
    try:
        response = await asyncio.wait_for(future, timeout)
        return response
    except asyncio.TimeoutError:
        await client.send_message(chat_id, "**◍ انتهى الوقت بدون رد\n√**")
        user_waiting.pop(sender_id, None)
        return None

async def can_promote_user(client: Client, chat_id: int, user_id: int, bot_username: str = None) -> bool:
    """
    تتحقق إذا كان المستخدم:
    - مالك الجروب (OWNER)
    - أو مشرفاً لديه صلاحية رفع المشرفين (can_promote_members = True)
    - أو هو المطور الأساسي للبوت (OWNER_ID)
    """
    try:
        if bot_username:
            OWNER_ID = await get_dev(bot_username)
            if user_id == OWNER_ID:
                return True

        member = await client.get_chat_member(chat_id, user_id)
        if member.status == ChatMemberStatus.OWNER:
            return True
        if member.status == ChatMemberStatus.ADMINISTRATOR:
            if member.privileges and member.privileges.can_promote_members:
                return True
        return False
    except Exception as e:
        logger.error(f"خطأ في can_promote_user: {e}")
        return False

# ======================== الأوامر الأصلية ========================
@Client.on_message(filters.command(["معلوماته","كشف"], ""))
async def kashf(client, message):
    bot_username = client.me.username
    OWNER_ID = await get_dev(bot_username)
    soesh = devchannel.get(bot_username) if devchannel.get(bot_username) else f"{source}"
    if await johned(client, message):
        return
    if message.reply_to_message:
       user_id = message.reply_to_message.from_user.id
       user = await client.get_chat_member(message.chat.id, user_id)  
       name = user.user.first_name
       CASER = await client.get_chat(user_id)
       bioo = CASER.bio
    elif message.text:
       username = message.text.split(" ", 1)[1]
       user = await client.get_chat_member(message.chat.id, username)
       name = user.user.first_name
       CASER = await client.get_chat(username)
       bioo = CASER.bio
    else:
       await message.reply_text("قم بإرسال الأمر مع اسم المستخدم الذي ترغب في رفعه")
       return
    await message.reply_text(f"❤ ¦ ɴᴀᴍᴇ : {user.user.mention}\n🥰 ¦ ᴜѕᴇ : @{user.user.username}\n🔥 ¦ ɪᴅ : {user.user.id}\n♥¦ ɪᴅ ᥇𝓲ꪮꪮ : [ُِِᥴَِɦُِᥲَِꪀَِꪀُِᥱَِᥣ َِ᥉ُِ᥆ُِᥙَِᖇُِᥴُِᥱ]({soesh})\n?? ¦ ɪᴅ ᴄʜᴀᴛ : {message.chat.id}\n☠️ ¦ ᴄʜᴀᴛ : {message.chat.title}\n💕 ¦ ɢʀᴏᴜᴘ : @{message.chat.username}\n", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(name, url=f"https://t.me/{user.user.username}")]]))

@Client.on_message(filters.command(["المالك", "صاحب الخرابه", "المنشي"], ""))
async def owner(client, message):
    bot_username = client.me.username
    OWNER_ID = await get_dev(bot_username)
    soesh = devchannel.get(bot_username) if devchannel.get(bot_username) else f"{source}"
    if await johned(client, message):
        return 
    x = []
    async for m in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        if m.status == ChatMemberStatus.OWNER:
            x.append(m.user.id)
    if len(x) != 0:        
        m = await client.get_users(int(x[0]))
        if m.photo:
            async for photo in client.get_chat_photos(x[0], limit=1):
                await message.reply_photo(
                    photo.file_id,
                    caption=(
                        f"🧞‍♂️ ¦𝙺𝙸𝙽𝙶 : {m.first_name}\n"
                        f"🎯 ¦𝚄𝚂𝙴𝚁 : @{m.username}\n"
                        f"🎃 ¦𝙸𝙳 : {m.id}\n"
                        f"✨ ¦𝙲𝙷𝙰𝚃: {message.chat.title}\n"
                        f"♻️ ¦𝙸𝙳.𝙲𝙷𝙰𝚃 : {message.chat.id}\n"
                        f"😎 ¦ ُِᥴَِɦُِᥲَِꪀَِꪀُِᥱَِᥣ َِ᥉ُِ᥆ُِᥙَِᖇُِᥴُِᥱ"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(m.first_name, url=f"https://t.me/{m.username}")]]
                    )
                )
        else:
            await message.reply_text(
                f"🧞‍♂️ ¦𝙺𝙸𝙽𝙶 : {m.first_name}\n"
                f"🎯 ¦𝚄𝚂𝙴𝚁 : @{m.username}\n"
                f"🎃 ¦𝙸𝙳 : `{m.id}`\n"
                f"✨ ¦𝙲𝙷𝙰𝚃: {message.chat.title}\n"
                f"♻️ ¦𝙸𝙳.𝙲𝙷𝙰𝚃 : `{message.chat.id}`\n"
                f"😎 ¦ ُِᥴَِɦُِᥲَِꪀَِꪀُِᥱَِᥣ َِ᥉ُِ᥆ُِᥙَِᖇُِᥴُِᥱ",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(m.first_name, url=f"https://t.me/{m.username}")]])
            )
    else:
        await message.reply_text("المالك غير موجود أو محذوف.")

@Client.on_message(filters.command(["قفل الايدي", "تعطيل الايدي"], ""), group=73)
async def iddlock(client, message):
    if await johned(client, message):
        return
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    if chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or message.from_user.username in wenru or message.from_user.username in caes:
        if message.chat.id not in id_enabled:
            return await message.reply_text("الايدي معطل من قبل 🔒")
        id_enabled.remove(message.chat.id)
        return await message.reply_text("تم تعطيل الأيدي ❤🔒")
    else:
        return await message.reply_text(f"عذراً عزيزي {message.from_user.mention}\nهذا الأمر لا يخصك ✨♥")

@Client.on_message(filters.command(["فتح الايدي", "تفعيل الايدي"], ""), group=703)
async def iddopen(client, message):
    if await johned(client, message):
        return
    chek = await client.get_chat_member(message.chat.id, message.from_user.id)
    if chek.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] or message.from_user.username in wenru or message.from_user.username in caes:
        if message.chat.id in id_enabled:
            return await message.reply_text("الايدي مفعل من قبل ✅")
        id_enabled.append(message.chat.id)
        return await message.reply_text("تم تفعيل الأيدي ❤⚡")
    else:
        return await message.reply_text(f"عذراً عزيزي {message.from_user.mention}\nهذا الأمر لا يخصك ✨♥")

@Client.on_message(filters.command(["ايدي", "الايدي", "ا"], ""), group=713)
async def iddd(client, message):
    if await johned(client, message):
        return
    if message.chat.id not in id_enabled:
        return await message.reply_text("الايدي تم تعطيله، اطلب من الادمن تفعيله 😊♥️")
    if message.from_user.photo:
        usr = await client.get_chat(message.from_user.id)
        photo = usr.photo.big_file_id
        photo = await client.download_media(photo)
        await message.reply_photo(
            photo=photo,
            caption=f"""╭⎋¦ ᚐ𝙽𝙰𝙼𝙴 : {message.from_user.mention}
╰⊚ᚐ ᴜsᴇʀ : @{message.from_user.username}
╭⎋ ɪᴅ : {message.from_user.id}
╰⊚ᚐ ʙɪᴏ : {usr.bio if usr and usr.bio else 'لا يوجد'}  
♥️ ¦ 𝙲𝙷𝙰𝚃 : {message.chat.title}
♻️ ¦ 𝙸𝙳.𝙶𝚁𝙾𝚄𝙿 : {message.chat.id}""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(message.from_user.first_name, url=f"https://t.me/{message.from_user.username}")]]
            )
        )
    else:
        usr = await client.get_chat(message.from_user.id)
        await message.reply_text(
            text=f"""╭⎋¦ᚐ𝙽𝙰𝙼𝙴 : {message.from_user.mention}
╰⊚ᚐᴜsᴇʀᚐ : @{message.from_user.username}
╭⎋ɪᴅᚐ : {message.from_user.id}
╰⊚ᚐʙɪᴏᚐ : {usr.bio if usr and usr.bio else 'لا يوجد'}
♥ ¦ 𝙲𝙷𝙰𝚃 : {message.chat.title}
♻️ ¦ 𝙸𝙳.𝙶𝚁𝙾𝚄𝙿 : {message.chat.id}""",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(message.from_user.first_name, url=f"https://t.me/{message.from_user.username}")]]
            )
        )

@Client.on_message(filters.regex(r"^\.$"))
async def tabati(client, message):
    await message.reply_text("**صلى على النبي وتبسم ❤🥺**")

@Client.on_message(filters.command(["المشرفين", "الادمنيه", "الادمن"], ""))
async def list_admins(client, message):
    if await johned(client, message):
        return
    chat_id = message.chat.id
    try:
        admins_list = []
        async for member in client.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
            if member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER):
                admin_info = f"• {member.user.mention}"
                if member.custom_title:
                    admin_info += f" (لقب: {member.custom_title})"
                admins_list.append(admin_info)
        if not admins_list:
            await message.reply_text("لا يوجد مشرفين في هذه المجموعة.")
        else:
            text = "**قائمة المشرفين في المجموعة:**\n\n" + "\n".join(admins_list)
            await message.reply_text(text)
    except Exception as e:
        await message.reply_text(f"حدث خطأ أثناء جلب المشرفين: {e}")

@Client.on_chat_member_updated(filters.group, group=4545417815)
async def welcome_handler(client: Client, chat_member_updated: ChatMemberUpdated):
    global welcome_enabled
    try:
        if not welcome_enabled:
            return
        if not chat_member_updated.new_chat_member:
            return
        if chat_member_updated.new_chat_member.status == ChatMemberStatus.BANNED:
            kicked_by = chat_member_updated.new_chat_member.restricted_by
            user = chat_member_updated.new_chat_member.user
            chat_id = chat_member_updated.chat.id
            if kicked_by is None or kicked_by.is_self:
                return
            bot_username = client.me.username
            OWNER_ID = await get_dev(bot_username)
            zombie_id = OWNER_ID
            if kicked_by.id != zombie_id:
                admin_id = kicked_by.id
                admin_name = kicked_by.first_name
                user_mention = f"[{user.first_name}](tg://user?id={user.id})"
                admin_mention = f"[{admin_name}](tg://user?id={admin_id})"
                message_text = (
                    f"**◍ قام أحد المشرفين بطرد مستخدم\n**"
                    f"**◍ المستخدم: {user_mention}\n**"
                    f"**◍ الايدي: `{user.id}`\n**"
                    f"**◍ المشرف المسؤول: {admin_mention}\n**"
                    f"**√**"
                )
                try:
                    await client.ban_chat_member(chat_id, admin_id)
                    message_text += "\n❌ تم حظر المشرف بسبب تجاوز الحد المسموح به!"
                except Exception:
                    message_text += "\n⚠️ لم يتمكن البوت من حظر المشرف!"
                await client.send_message(chat_id, message_text)
    except Exception as e:
        logger.error(f"Error in welcome_handler: {e}")

@Client.on_message(filters.command("تعديل صلاحيات", "") & filters.group)
async def edit_admin_permissions(client, message):
    bot_username = client.me.username
    # التحقق من صلاحية المستخدم (مالك الجروب / مشرف بصلاحيات كاملة / مطور)
    if not await can_promote_user(client, message.chat.id, message.from_user.id, bot_username):
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك الجروب أو مشرف لديه صلاحية رفع المشرفين أو مطور البوت لاستخدام هذا الأمر\n√**")
    
    if message.reply_to_message and message.reply_to_message.from_user:
        target_admin = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        username = message.text.split()[2]
        try:
            target_admin = await client.get_users(username.strip("@"))
        except:
            await message.reply_text("❌ لم يتم العثور على المستخدم")
            return
    else:
        ask1 = await zom_ask(client, message, "**◍ يرجى إرسال معرف المشرف أو الرد على رسالته\n√**")
        try:
            target_admin = await client.get_users(ask1.text)
        except:
            await message.reply_text("❌ بيانات المستخدم غير صحيحة")
            return
    try:
        admin_status = await client.get_chat_member(message.chat.id, target_admin.id)
        if admin_status.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            await message.reply_text("⚠️ هذا العضو ليس مشرفاً في المجموعة")
            return
    except:
        await message.reply_text("❌ حدث خطأ في التحقق من الصلاحيات")
        return
    buttons = [
        [
            InlineKeyboardButton("🗑️ حذف الرسائل", callback_data=f"editperm_del_{target_admin.id}"),
            InlineKeyboardButton("🔇 تقييد أعضاء", callback_data=f"editperm_ban_{target_admin.id}")
        ],
        [
            InlineKeyboardButton("📌 تثبيت رسائل", callback_data=f"editperm_pin_{target_admin.id}"),
            InlineKeyboardButton("📞 إدارة المكالمات", callback_data=f"editperm_call_{target_admin.id}")
        ],
        [
            InlineKeyboardButton("➕ دعوة مستخدمين", callback_data=f"editperm_invite_{target_admin.id}"),
            InlineKeyboardButton("✏️ تعديل المجموعة", callback_data=f"editperm_info_{target_admin.id}")
        ],
        [
            InlineKeyboardButton("🔼 رفع مشرفين", callback_data=f"editperm_promo_{target_admin.id}")
        ],
        [
            InlineKeyboardButton("✅ حفظ التعديلات", callback_data=f"save_perms_{target_admin.id}")
        ]
    ]
    current_perms = admin_status.privileges
    perm_status = {
        "del": "✅" if current_perms.can_delete_messages else "❌",
        "ban": "✅" if current_perms.can_restrict_members else "❌",
        "pin": "✅" if current_perms.can_pin_messages else "❌",
        "call": "✅" if current_perms.can_manage_video_chats else "❌",
        "invite": "✅" if current_perms.can_invite_users else "❌",
        "info": "✅" if current_perms.can_change_info else "❌",
        "promo": "✅" if current_perms.can_promote_members else "❌"
    }
    buttons[0][0].text = f"{perm_status['del']} حذف الرسائل"
    buttons[0][1].text = f"{perm_status['ban']} تقييد أعضاء"
    buttons[1][0].text = f"{perm_status['pin']} تثبيت رسائل"
    buttons[1][1].text = f"{perm_status['call']} إدارة المكالمات"
    buttons[2][0].text = f"{perm_status['invite']} دعوة مستخدمين"
    buttons[2][1].text = f"{perm_status['info']} تعديل المجموعة"
    buttons[3][0].text = f"{perm_status['promo']} رفع مشرفين"
    admin_edit_cache[f"edit_{target_admin.id}"] = {
        "chat_id": message.chat.id,
        "admin_id": target_admin.id,
        "promoter_id": message.from_user.id,
        "current_perms": current_perms,
        "new_perms": {
            "del": current_perms.can_delete_messages,
            "ban": current_perms.can_restrict_members,
            "pin": current_perms.can_pin_messages,
            "call": current_perms.can_manage_video_chats,
            "invite": current_perms.can_invite_users,
            "info": current_perms.can_change_info,
            "promo": current_perms.can_promote_members
        }
    }
    await message.reply_text(
        f"⚙️ **تعديل صلاحيات المشرف:**\n"
        f"👤 المستخدم: {target_admin.mention}\n"
        f"🔽 اختر الصلاحيات المطلوبة:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("^editperm_.*"))
async def update_permission(client, callback):
    data = callback.data
    _, perm, admin_id = data.split('_')
    cache_key = f"edit_{admin_id}"
    if cache_key not in admin_edit_cache:
        await callback.answer("❌ انتهت الجلسة!", show_alert=True)
        return
    perm_names = {
        "del": "حذف الرسائل",
        "ban": "تقييد الأعضاء",
        "pin": "تثبيت الرسائل",
        "call": "إدارة المكالمات",
        "invite": "دعوة مستخدمين",
        "info": "تعديل المجموعة",
        "promo": "رفع مشرفين"
    }
    current_state = admin_edit_cache[cache_key]["new_perms"][perm]
    admin_edit_cache[cache_key]["new_perms"][perm] = not current_state
    new_state = "✅" if not current_state else "❌"
    button_icons = {
        "del": "🗑️",
        "ban": "🔇",
        "pin": "📌",
        "call": "📞",
        "invite": "➕",
        "info": "✏️",
        "promo": "🔼"
    }
    for row in callback.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data.endswith(f"{perm}_{admin_id}"):
                button.text = f"{button_icons[perm]} {perm_names[perm]}: {new_state}"
                break
    await callback.message.edit_reply_markup(callback.message.reply_markup)
    await callback.answer(f"تم تغيير صلاحية {perm_names[perm]}")

@Client.on_callback_query(filters.regex("^save_perms_.*"))
async def save_permissions(client, callback):
    admin_id = callback.data.split('_')[-1]
    cache_key = f"edit_{admin_id}"
    if cache_key not in admin_edit_cache:
        await callback.answer("❌ انتهت الجلسة!", show_alert=True)
        return
    data = admin_edit_cache[cache_key]
    new_perms = data["new_perms"]
    try:
        await client.promote_chat_member(
            chat_id=data["chat_id"],
            user_id=int(admin_id),
            privileges=ChatPrivileges(
                can_delete_messages=new_perms["del"],
                can_restrict_members=new_perms["ban"],
                can_pin_messages=new_perms["pin"],
                can_manage_video_chats=new_perms["call"],
                can_invite_users=new_perms["invite"],
                can_change_info=new_perms["info"],
                can_promote_members=new_perms["promo"]
            )
        )
        changes = []
        perm_display = {
            "del": "حذف الرسائل",
            "ban": "تقييد الأعضاء",
            "pin": "تثبيت الرسائل",
            "call": "إدارة المكالمات",
            "invite": "دعوة مستخدمين",
            "info": "تعديل المجموعة",
            "promo": "رفع مشرفين"
        }
        for perm, name in perm_display.items():
            current_value = getattr(data["current_perms"], f"can_{perm_map(perm)}", False)
            if new_perms[perm] != current_value:
                changes.append(f"◍ {name}: {'✅' if new_perms[perm] else '❌'}")
        admin_user = await client.get_users(int(admin_id))
        promoter_user = await client.get_users(data["promoter_id"])
        report_text = (
            f"🎯 **تقرير تعديل الصلاحيات**\n\n"
            f"👤 المشرف: {admin_user.mention}\n"
            f"👮‍♂️ المعدل: {promoter_user.mention}\n\n"
            f"📋 التغييرات:\n" + "\n".join(changes) + "\n\n"
            f"⏱️ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        await callback.message.reply_text(report_text)
        await callback.message.delete()
        del admin_edit_cache[cache_key]
        await callback.answer("✅ تم التحديث بنجاح!", show_alert=True)
    except Exception as e:
        error_msg = (
            "⚠️ **حدث خطأ**\n\n"
            "تعذر تحديث صلاحيات المشرف\n"
            f"السبب: {str(e)}\n\n"
            "يرجى التحقق من صلاحيات البوت والمحاولة مرة أخرى"
        )
        await callback.message.reply_text(error_msg)
        await callback.answer("❌ فشل في الحفظ!", show_alert=True)

@Client.on_message(filters.command(["تعطيل الرفع", "قفل الرفع"], "") & filters.group, group=1333360)
async def maaafock(client: Client, message):
    bot_username = client.me.username
    if not await can_promote_user(client, message.chat.id, message.from_user.id, bot_username):
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك الجروب أو مشرف لديه صلاحية رفع المشرفين أو مطور البوت لاستخدام هذا الأمر\n√**")
    if message.chat.id in promotion_lock:
        return await message.reply_text("**◍ الرفع معطل من قبل\n√**")
    promotion_lock.append(message.chat.id)
    locks["promotion_lock"] = promotion_lock
    save_locks(locks)
    return await message.reply_text("**◍ تم تعطيل الرفع بنجاح\n√**")

@Client.on_message(filters.command(["فتح الرفع", "تفعيل الرفع"], "") & filters.group, group=1211028)
async def maaafpen(client: Client, message):
    bot_username = client.me.username
    if not await can_promote_user(client, message.chat.id, message.from_user.id, bot_username):
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك الجروب أو مشرف لديه صلاحية رفع المشرفين أو مطور البوت لاستخدام هذا الأمر\n√**")
    if message.chat.id not in promotion_lock:
        return await message.reply_text("**◍ الرفع مفعل من قبل\n√**")
    promotion_lock.remove(message.chat.id)
    locks["promotion_lock"] = promotion_lock
    save_locks(locks)
    return await message.reply_text("**◍ تم تفعيل الرفع بنجاح\n√**")

@Client.on_message(filters.command("رفع مشرف", "") & filters.group, group=1212474777777)
async def promote_admin(client, message):
    bot_username = client.me.username
    if message.chat.id in promotion_lock:
        return await message.reply_text("**◍ الرفع معطل اطلب من منشئ او مالك تفعيله\n√**")
    if not await can_promote_user(client, message.chat.id, message.from_user.id, bot_username):
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك الجروب أو مشرف لديه صلاحية رفع المشرفين أو مطور البوت لاستخدام هذا الأمر\n√**")
    
    args = message.text.split(maxsplit=2)
    user = None
    title = None
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        if len(args) == 2:
            ask_title = await zom_ask(client, message, "**◍ أرسل اللقب الجديد للمشرف\n√**")
            title = ask_title.text
        else:
            title = args[2]
    elif len(args) >= 3:
        target, title = args[1], args[2]
        try:
            if target.startswith("@"):
                user = await client.get_users(target)
            elif target.isdigit():
                user = await client.get_users(int(target))
        except Exception:
            return await message.reply("❌ لا يمكن العثور على المستخدم")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن ايدي أو يوزر المستخدم\n√**")
        try:
            user = await client.get_users(ask.text.strip())
        except Exception:
            return await message.reply("❌ معرف المستخدم غير صحيح")
        ask_title = await zom_ask(client, message, "**◍ أرسل اللقب الجديد للمشرف\n√**")
        title = ask_title.text
    await client.promote_chat_member(
        message.chat.id,
        user.id,
        ChatPrivileges(
            can_delete_messages=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_manage_video_chats=True
        )
    )
    await client.set_administrator_title(message.chat.id, user.id, title)
    temp_storage[f"perms_{user.id}"] = {
        "chat_id": message.chat.id,
        "user": user,
        "promoter": message.from_user,
        "title": title,
        "permissions": {
            "delete": True,
            "restrict": False,
            "invite": True,
            "pin": True,
            "manage": True,
            "change": False,
            "promote": False
        }
    }
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("تعديل الصلاحيات 🚧", callback_data=f"permssions {user.id} {message.from_user.id}")
    ]])
    await message.reply(
        f"✅ تم رفع {user.mention} كمشرف بلقب: `{title}`",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^permssions (\d+) (\d+)$"))
async def open_permission_editor(client, callback):
    user_id, promoter_id = callback.matches[0].group(1), callback.matches[0].group(2)
    temp_data = temp_storage.get(f"perms_{user_id}")
    if not temp_data:
        await callback.answer("❌ لا يوجد بيانات محفوظة لهذا المستخدم.", show_alert=True)
        return
    if str(callback.from_user.id) != promoter_id:
        return await callback.answer("❌ هذا الخيار متاح فقط لمن قام برفع المشرف.", show_alert=True)
    perm_names = {
        "delete": "حذف الرسائل",
        "restrict": "تقييد الأعضاء",
        "invite": "دعوة مستخدمين",
        "pin": "تثبيت الرسائل",
        "manage": "إدارة المكالمات",
        "change": "تعديل المجموعة",
        "promote": "رفع مشرفين"
    }
    keyboard = []
    for perm, name in perm_names.items():
        state = "✅" if temp_data["permissions"][perm] else "❌"
        keyboard.append([InlineKeyboardButton(f"{name}: {state}", callback_data=f"perm_{perm}_{user_id}")])
    keyboard.append([InlineKeyboardButton("تأكيد الصلاحيات", callback_data=f"confirm_perms_{user_id}")])
    await callback.message.edit_text(
        f"⚙️ تعديل صلاحيات المشرف:\n👤 {temp_data['user'].mention}\n\n"
        f"اختر أو عدّل الصلاحيات حسب الحاجة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex(r"^perm_(delete|restrict|invite|pin|manage|change|promote)_(\d+)$"))
async def handle_perm_buttons(client, callback):
    perm_type = callback.matches[0].group(1)
    user_id = callback.matches[0].group(2)
    temp_data = temp_storage.get(f"perms_{user_id}")
    if not temp_data:
        await callback.answer("❌ انتهت صلاحية الجلسة!", show_alert=True)
        return
    if callback.from_user.id != temp_data["promoter"].id:
        await callback.answer("❌ هذا الأمر خاص بمن قام برفع المشرف فقط.", show_alert=True)
        return
    temp_data["permissions"][perm_type] = not temp_data["permissions"][perm_type]
    perm_names = {
        "delete": "حذف الرسائل",
        "restrict": "تقييد الأعضاء",
        "invite": "دعوة مستخدمين",
        "pin": "تثبيت الرسائل",
        "manage": "إدارة المكالمات",
        "change": "تعديل المجموعة",
        "promote": "رفع مشرفين"
    }
    keyboard = []
    for perm, name in perm_names.items():
        state = "✅" if temp_data["permissions"][perm] else "❌"
        keyboard.append([InlineKeyboardButton(f"{name}: {state}", callback_data=f"perm_{perm}_{user_id}")])
    keyboard.append([InlineKeyboardButton("تأكيد الصلاحيات", callback_data=f"confirm_perms_{user_id}")])
    await callback.message.edit_reply_markup(InlineKeyboardMarkup(keyboard))
    await callback.answer(f"تم تعديل صلاحية {perm_names[perm_type]}")

@Client.on_callback_query(filters.regex(r"^confirm_perms_(\d+)$"))
async def handle_confirm_button(client, callback):
    user_id = callback.matches[0].group(1)
    temp_data = temp_storage.get(f"perms_{user_id}")
    if not temp_data:
        await callback.answer("❌ انتهت صلاحية الجلسة!", show_alert=True)
        return
    if callback.from_user.id != temp_data["promoter"].id:
        await callback.answer("❌ هذا الأمر خاص بمن قام برفع المشرف فقط.", show_alert=True)
        return
    title = temp_data["title"]
    await client.promote_chat_member(
        chat_id=temp_data["chat_id"],
        user_id=int(user_id),
        privileges=ChatPrivileges(
            can_delete_messages=temp_data["permissions"]["delete"],
            can_restrict_members=temp_data["permissions"]["restrict"],
            can_invite_users=temp_data["permissions"]["invite"],
            can_pin_messages=temp_data["permissions"]["pin"],
            can_manage_video_chats=temp_data["permissions"]["manage"],
            can_change_info=temp_data["permissions"]["change"],
            can_promote_members=temp_data["permissions"]["promote"]
        )
    )
    await client.set_administrator_title(
        temp_data["chat_id"],
        int(user_id),
        title
    )
    active_perms = []
    for perm, name in {
        "delete": "حذف الرسائل",
        "restrict": "تقييد الأعضاء", 
        "invite": "دعوة المستخدمين",
        "pin": "تثبيت الرسائل",
        "manage": "إدارة المكالمات",
        "change": "تعديل المجموعة",
        "promote": "رفع المشرفين"
    }.items():
        if temp_data["permissions"][perm]:
            active_perms.append(f"◍ {name}")
    now = datetime.now(ZoneInfo("Africa/Cairo"))
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    await callback.message.reply_text(
        f"**◍ تم رفع المشرف بنجاح**\n"
        f"**◍ المشرف : {temp_data['user'].mention}**\n"
        f"**◍ اللقب : {title}**\n"
        f"**◍ بواسطة : {temp_data['promoter'].mention}**\n"
        f"**◍ التاريخ : {date_str}**\n"
        f"**◍ الوقت : {time_str}**\n"
        f"**√**"
    )
    await callback.message.delete()
    del temp_storage[f"perms_{user_id}"]

@Client.on_message(filters.command("رفع مشرف", "") & filters.channel, group=12878712474)
async def tasfaya(client, message):
    input_parts = message.text.split(maxsplit=2)
    if len(input_parts) >= 3:
        user_input = input_parts[2].strip().replace("@", "")
    else:
        ask1 = await zom_ask(client, message, "**◍ أرسل الآن يوزر أو آيدي المستخدم الذي تريد رفعه مشرف\n√**")
        user_input = ask1.text.strip().replace("@", "")
    try:
        user = await client.get_users(user_input)
    except Exception:
        return await message.reply("❌ فشل في جلب المستخدم. تأكد من صحة اليوزر أو الآيدي.")
    try:
        await client.promote_chat_member(
            chat_id=message.chat.id,
            user_id=user.id,
            privileges=ChatPrivileges(
                can_promote_members=False,
                can_manage_video_chats=True,
                can_post_messages=True,
                can_invite_users=True,
                can_edit_messages=True,
                can_delete_messages=True,
                can_change_info=False
            )
        )
        await message.reply(f"✅ تم رفع {user.mention} مشرف بنجاح.")
    except Exception as e:
        await message.reply(f"❌ فشل في رفع المشرف:\n{e}")

@Client.on_message(filters.command(["صلاحياتي"], "") & filters.group, group=115354)
async def aarprivileges(client, message):
    is_subscribed = await checkg_member_status(message.from_user.id, message, client)
    if not is_subscribed:
        return False
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else "None"
    cae = await client.get_chat_member(chat_id, user_id)
    status = cae.status if cae else None
    if status == ChatMemberStatus.OWNER:
        await message.reply_text("أنت مالك الجروب")
    elif status == ChatMemberStatus.MEMBER:
        await message.reply_text("أنت عضو حقير")
    else:
        privileges = cae.privileges if cae else None 
        can_promote_members = "✅" if (privileges and privileges.can_promote_members) else "❌"
        can_manage_video_chats = "✅" if (privileges and privileges.can_manage_video_chats) else "❌"
        can_pin_messages = "✅" if (privileges and privileges.can_pin_messages) else "❌"
        can_invite_users = "✅" if (privileges and privileges.can_invite_users) else "❌"
        can_restrict_members = "✅" if (privileges and privileges.can_restrict_members) else "❌"
        can_delete_messages = "✅" if (privileges and privileges.can_delete_messages) else "❌"
        can_change_info = "✅" if (privileges and privileges.can_change_info) else "❌"
        text = "صلاحياتك في الجروب:\n\n"
        text += f"ترقية الأعضاء: {can_promote_members}\n"
        text += f"إدارة الدردشات الصوتية: {can_manage_video_chats}\n"
        text += f"تثبيت الرسائل: {can_pin_messages}\n"
        text += f"دعوة المستخدمين: {can_invite_users}\n"
        text += f"تقييد الأعضاء: {can_restrict_members}\n"
        text += f"حذف الرسائل: {can_delete_messages}\n"
        text += f"تغيير معلومات الجروب: {can_change_info}\n"
        await message.reply_text(text)

@Client.on_message(filters.command(["لقبي"], "") & filters.group, group=7272727866)
async def mytitle(client, message):
    is_subscribed = await checkg_member_status(message.from_user.id, message, client)
    if not is_subscribed:
        return False
    user_id = message.from_user.id if message.from_user else "None"
    chat_id = message.chat.id
    user = await client.get_chat_member(chat_id, user_id)    
    if user.status in [ChatMemberStatus.OWNER]:
        await message.reply_text("مالك الجروب")
    elif user.status == ChatMemberStatus.MEMBER:
        await message.reply_text("عضو حقير")
    elif user.status == ChatMemberStatus.ADMINISTRATOR:
        title = user.custom_title if user.custom_title else "مشرف"
        await message.reply_text(f"{title}")

@Client.on_message(filters.command(["لقبه"], "") & filters.group, group=72727866)
async def htitle(client, message):
    is_subscribed = await checkg_member_status(message.from_user.id, message, client)
    if not is_subscribed:
        return False
    if not message.reply_to_message:
        return await message.reply_text("قم بالرد على الشخص الذي تريد معرفة لقبه")
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    user = await client.get_chat_member(chat_id, user_id)    
    if user.status in [ChatMemberStatus.OWNER]:
        await message.reply_text("مالك الجروب")
    elif user.status == ChatMemberStatus.MEMBER:
        await message.reply_text("عضو حقير")
    elif user.status == ChatMemberStatus.ADMINISTRATOR:
        title = user.custom_title if user.custom_title else "مشرف"
        await message.reply_text(f"{title}")

@Client.on_message((filters.group | filters.private | filters.channel) & ~filters.service, group=62652)
async def catch_response(client: Client, message: Message):
    try:
        sender_id = message.from_user.id if message.from_user else message.sender_chat.id
        if sender_id in user_waiting:
            future = user_waiting.pop(sender_id)
            if not future.done():
                future.set_result(message)
    except Exception:
        pass