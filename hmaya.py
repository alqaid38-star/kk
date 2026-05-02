import asyncio
import json
import os
import re
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges, CallbackQuery, Message
from pyrogram.errors import FloodWait
from Source.Data import get_dev

logger = logging.getLogger(__name__)

# ======================== المتغيرات الأساسية ========================
OWNER_ID = None
sourse_dev = None
zombie_id = None
dev = []  # قائمة المطورين الإضافيين

# متغيرات إضافية من ratab.py
devchannel = {}
source = "https://t.me/source_Asyuti"
id_enabled = []
wenru = []
caes = []
welcome_enabled = True
promotion_lock = []
user_waiting = {}
temp_storage = {}
admin_edit_cache = {}

LOCK_FILE = "locks_data.json"
RANKS_FILE = "ranks_data.json"

# ======================== نظام الرتب (من ratab.py) ========================
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

def load_ranks():
    default = {
        "main_developers": [],
        "sub_developers": [],
        "group_owners": {},
        "group_creators": {},
        "group_admins": {},
        "group_vips": {}
    }
    if os.path.exists(RANKS_FILE):
        try:
            with open(RANKS_FILE, "r") as f:
                data = json.load(f)
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except:
            return default
    else:
        with open(RANKS_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default

def save_ranks(data):
    with open(RANKS_FILE, "w") as f:
        json.dump(data, f, indent=4)

ranks_data = load_ranks()

# دوال الرتب
def add_main_developer(user_id):
    if user_id not in ranks_data["main_developers"]:
        ranks_data["main_developers"].append(user_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_main_developer(user_id):
    if user_id in ranks_data["main_developers"]:
        ranks_data["main_developers"].remove(user_id)
        save_ranks(ranks_data)
        return True
    return False

def get_main_developers():
    return ranks_data["main_developers"]

def is_main_developer(user_id):
    return user_id in ranks_data["main_developers"]

def add_sub_developer(user_id):
    if user_id not in ranks_data["sub_developers"]:
        ranks_data["sub_developers"].append(user_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_sub_developer(user_id):
    if user_id in ranks_data["sub_developers"]:
        ranks_data["sub_developers"].remove(user_id)
        save_ranks(ranks_data)
        return True
    return False

def get_sub_developers():
    return ranks_data["sub_developers"]

def is_sub_developer(user_id):
    return user_id in ranks_data["sub_developers"]

def add_group_owner(group_id, owner_id):
    group_id = str(group_id)
    if group_id not in ranks_data["group_owners"]:
        ranks_data["group_owners"][group_id] = []
    if owner_id not in ranks_data["group_owners"][group_id]:
        ranks_data["group_owners"][group_id].append(owner_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_group_owner(group_id, owner_id):
    group_id = str(group_id)
    if group_id in ranks_data["group_owners"] and owner_id in ranks_data["group_owners"][group_id]:
        ranks_data["group_owners"][group_id].remove(owner_id)
        if not ranks_data["group_owners"][group_id]:
            del ranks_data["group_owners"][group_id]
        save_ranks(ranks_data)
        return True
    return False

def get_group_owners(group_id):
    group_id = str(group_id)
    return ranks_data["group_owners"].get(group_id, [])

def is_group_owner(group_id, user_id):
    group_id = str(group_id)
    return user_id in ranks_data["group_owners"].get(group_id, [])

def add_group_creator(group_id, creator_id):
    group_id = str(group_id)
    if group_id not in ranks_data["group_creators"]:
        ranks_data["group_creators"][group_id] = []
    if creator_id not in ranks_data["group_creators"][group_id]:
        ranks_data["group_creators"][group_id].append(creator_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_group_creator(group_id, creator_id):
    group_id = str(group_id)
    if group_id in ranks_data["group_creators"] and creator_id in ranks_data["group_creators"][group_id]:
        ranks_data["group_creators"][group_id].remove(creator_id)
        if not ranks_data["group_creators"][group_id]:
            del ranks_data["group_creators"][group_id]
        save_ranks(ranks_data)
        return True
    return False

def get_group_creators(group_id):
    group_id = str(group_id)
    return ranks_data["group_creators"].get(group_id, [])

def is_group_creator(group_id, user_id):
    group_id = str(group_id)
    return user_id in ranks_data["group_creators"].get(group_id, [])

def add_group_admin(group_id, admin_id):
    group_id = str(group_id)
    if group_id not in ranks_data["group_admins"]:
        ranks_data["group_admins"][group_id] = []
    if admin_id not in ranks_data["group_admins"][group_id]:
        ranks_data["group_admins"][group_id].append(admin_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_group_admin(group_id, admin_id):
    group_id = str(group_id)
    if group_id in ranks_data["group_admins"] and admin_id in ranks_data["group_admins"][group_id]:
        ranks_data["group_admins"][group_id].remove(admin_id)
        if not ranks_data["group_admins"][group_id]:
            del ranks_data["group_admins"][group_id]
        save_ranks(ranks_data)
        return True
    return False

def get_group_admins(group_id):
    group_id = str(group_id)
    return ranks_data["group_admins"].get(group_id, [])

def is_group_admin(group_id, user_id):
    group_id = str(group_id)
    return user_id in ranks_data["group_admins"].get(group_id, [])

def add_group_vip(group_id, vip_id):
    group_id = str(group_id)
    if group_id not in ranks_data["group_vips"]:
        ranks_data["group_vips"][group_id] = []
    if vip_id not in ranks_data["group_vips"][group_id]:
        ranks_data["group_vips"][group_id].append(vip_id)
        save_ranks(ranks_data)
        return True
    return False

def remove_group_vip(group_id, vip_id):
    group_id = str(group_id)
    if group_id in ranks_data["group_vips"] and vip_id in ranks_data["group_vips"][group_id]:
        ranks_data["group_vips"][group_id].remove(vip_id)
        if not ranks_data["group_vips"][group_id]:
            del ranks_data["group_vips"][group_id]
        save_ranks(ranks_data)
        return True
    return False

def get_group_vips(group_id):
    group_id = str(group_id)
    return ranks_data["group_vips"].get(group_id, [])

def is_group_vip(group_id, user_id):
    group_id = str(group_id)
    return user_id in ranks_data["group_vips"].get(group_id, [])

# ======================== دالة الصلاحية الموحدة ========================
async def check_permission(client, message, check_admin_only=False):
    """
    تتحقق من صلاحية المستخدم لاستخدام أوامر الحماية والإدارة.
    يسمح لـ:
    - مالك البوت (المطور الأساسي)
    - المطورين الأساسيين والثانويين
    - مشرفي التليجرام في المجموعة (أصحاب الرتب العالية)
    - الرتب المخصصة للبوت: مالك، منشئ، ادمن، مميز حسب صلاحيات كل أمر
    عند check_admin_only=False، يتم السماح لكل الرتب المذكورة.
    """
    if not message.from_user:
        return False
    user_id = message.from_user.id
    chat_id = message.chat.id

    # تحديث بيانات المطور الأساسي من قاعدة البيانات
    bot_username = client.me.username
    global OWNER_ID, sourse_dev, zombie_id, dev
    OWNER_ID = await get_dev(bot_username)
    sourse_dev = OWNER_ID
    zombie_id = OWNER_ID

    # 1. مالك البوت والمطورين المباشرين
    if user_id in [OWNER_ID, sourse_dev, zombie_id] + dev:
        return True
    if is_main_developer(user_id) or is_sub_developer(user_id):
        return True

    if check_admin_only:
        return False

    # 2. صلاحيات التليجرام الأصلية (مالك المجموعة أو مشرف فيها)
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return True
    except Exception:
        pass

    # 3. الرتب المخصصة للبوت (مالك، منشئ، ادمن، مميز)
    chat_id_str = str(chat_id)
    if is_group_owner(chat_id_str, user_id):
        return True
    if is_group_creator(chat_id_str, user_id):
        return True
    if is_group_admin(chat_id_str, user_id):
        return True
    if is_group_vip(chat_id_str, user_id):
        return True

    return False

# دوال مساعدة للتوافق مع الكود القديم
async def johned(client, message):
    return not await check_permission(client, message)

async def checkg_member_status(user_id, message, client):
    # يمكن تعديلها للتحقق من الاشتراك بقناة لاحقاً
    return True

# دوال محسنة للصلاحيات تستدعي دوال الرتب
def is_group_creator_fast(chat_id, user_id):
    return is_group_creator(str(chat_id), user_id)

def is_group_owner_fast(chat_id, user_id):
    return is_group_owner(str(chat_id), user_id)

def is_group_admin_fast(chat_id, user_id):
    return is_group_admin(str(chat_id), user_id)

# ======================== إعدادات ملف القفل (chat_locks.json) ========================
LOCK_FILE_CHAT = "chat_locks.json"

def load_locks_chat():
    default_data = {
        "dardasha": {},
        "mutaharek": {},
        "channel_lock": {},
        "videoo": {},
        "tawgeh": {},
        "photo_lock": {},
        "link_lock": {},
        "mentionn": {},
        "swear_lock": {},
        "sticker_lock": {},
        "muted_users": {},
        "english_lock": {},
        "emoji_lock": {},
        "clash_lock": {},
        "ban_lock": {},
        "id_lock": [],
        "id_photo_lock": [],
        "sorty_lock": [],
        "promotion_lock": [],
        "kickme_lock": []
    }
    try:
        if os.path.exists(LOCK_FILE_CHAT):
            with open(LOCK_FILE_CHAT, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                return data
        else:
            with open(LOCK_FILE_CHAT, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
            return default_data
    except Exception as e:
        print(f"حدث خطأ أثناء تحميل إعدادات الحماية: {e}")
        return default_data

def save_locks_chat(data):
    try:
        with open(LOCK_FILE_CHAT, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"حدث خطأ أثناء حفظ إعدادات الحماية: {e}")

locks = load_locks_chat()
dardasha = locks.get("dardasha", {})
mutaharek = locks.get("mutaharek", {})
videoo = locks.get("videoo", {})
mentionn = locks.get("mentionn", {})
tawgeh = locks.get("tawgeh", {})
channel_lock = locks.get("channel_lock", {})
link_lock = locks.get("link_lock", {})
photo_lock = locks.get("photo_lock", {})
sticker_lock = locks.get("sticker_lock", {})
swear_lock = locks.get("swear_lock", {})
english_lock = locks.get("english_lock", {})
emoji_lock = locks.get("emoji_lock", {})
clash_lock = locks.get("clash_lock", {})
muted_users = locks.get("muted_users", {})
id_lock = locks.get("id_lock", [])
id_photo_lock = locks.get("id_photo_lock", [])
sorty_lock = locks.get("sorty_lock", [])
promotion_lock_list = locks.get("promotion_lock", [])
kickme_lock = locks.get("kickme_lock", [])

# ======================== دالة انتظار الرد ========================
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

# ======================== أوامر الحماية (قفل/فتح) ========================
# جميع الأوامر التالية تستخدم check_permission بدلاً من الدوال الوهمية

# أمر تبتي
@Client.on_message(filters.command(["تبتي"], ""))
async def tabati(client, message):
    await message.reply_text("✅ البوت يعمل بكفاءة وبكل صلاحياته.")

# أمر المشرفين
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

# قفل الدردشة
@Client.on_message(filters.command(["قفل الدردشه","قفل الدردشة"], "") & filters.group, group=1212474987878)
async def lock_chat(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    
    chat_id = str(message.chat.id)
    
    if chat_id in dardasha:
        current_settings = dardasha[chat_id]
        await message.reply_text(
            f"⚠️ الدردشة مقفولة بالفعل\n"
            f"◍ العقوبة: {current_settings.get('punishment', 'حذف الرسائل')}\n"
            f"◍ النطاق: {'الكل' if current_settings.get('scope', 'all') == 'all' else 'الأعضاء فقط'}"
        )
        return
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("حذف الرسائل", callback_data=f"chat_choose_delete_{message.from_user.id}")],
        [InlineKeyboardButton("كتم المرسل", callback_data=f"chat_choose_mute_{message.from_user.id}")]
    ])
    
    await message.reply_text(
        f"◍ اختر طريقة العقاب لقفل الدردشة ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^chat_choose_(delete|mute)_(\d+)$"))
async def chat_choose_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[3])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[2]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"chat_confirm_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"chat_confirm_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع بما فيهم المشرفين\n"
        "- باستثناء المشرفين: تطبق على الأعضاء العاديين فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^chat_confirm_(delete|mute)_(all|members)_(\d+)$"))
async def chat_confirm_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    dardasha[chat_id] = {
        "punishment": action,
        "scope": scope
    }
    locks["dardasha"] = dardasha
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الدردشة بنجاح\n"
        f"◍ العقوبة: {'حذف الرسائل' if action == 'delete' else 'كتم المرسل'}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط (استثناء المشرفين)'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح الدردشه","فتح الدردشة"], "") & filters.group, group=1789212474)
async def unlock_chat(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in dardasha:
        await message.reply_text("⚠️ الدردشة غير مقفولة بالفعل!")
        return
    del dardasha[chat_id]
    locks["dardasha"] = dardasha
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح الدردشة بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.group, group=12897812474)
async def handle_chat_message(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in dardasha:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID, *dev) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        settings = dardasha[chat_id]
        punishment = settings.get("punishment", "delete")
        scope = settings.get("scope", "all")
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        if punishment == "delete":
            await message.delete()
            await client.send_message(message.chat.id, f"◍ عذراً {message.from_user.mention}، الدردشة مقفولة حالياً")
        elif punishment == "mute":
            await message.delete()
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ تم كتم {message.from_user.mention} لإرسال رسالة في الدردشة المقفولة")
    except Exception as e:
        print(f"Error handling chat message: {e}")

# قفل المتحركات
@Client.on_message(filters.command(["قفل المتحركات"], "") & filters.group, group=1289712474)
async def lock_gifs(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in mutaharek:
        current_punishment, current_scope = mutaharek[chat_id]
        await message.reply_text(
            f"⚠️ المتحركات مقفولة بالفعل\n"
            f"◍ العقوبة الحالية: {current_punishment}\n"
            f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"choose_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"choose_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"choose_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل المتحركات ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^choose_(mute|restrict|ban)_(\d+)$"))
async def choose_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع بما فيهم المشرفين\n"
        "- باستثناء المشرفين: تطبق على الأعضاء العاديين فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_punishment(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[3])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[1], callback_query.data.split('_')[2]
    mutaharek[chat_id] = [action, scope]
    locks["mutaharek"] = mutaharek
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل المتحركات بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط (استثناء المشرفين)'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح المتحركات"], "") & filters.group, group=1289712475)
async def unlock_gifs(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in mutaharek:
        await message.reply_text("⚠️ المتحركات غير مقفولة بالفعل!")
        return
    del mutaharek[chat_id]
    locks["mutaharek"] = mutaharek
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح المتحركات بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.animation & filters.group, group=14782124)
async def handle_gif(client, message):
    # نفس المنطق السابق مع التحقق من الرتب
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in mutaharek:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = mutaharek[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ تم كتم {message.from_user.mention} لإرسال متحركات")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال متحركات")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ تم طرد {message.from_user.mention} لإرسال متحركات")
    except Exception as e:
        print(f"Error handling GIF: {e}")

# قفل الكلايش
@Client.on_message(filters.command(["قفل الكلايش"], "") & filters.group, group=2002501)
async def lock_clash(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر")
    chat_id = str(message.chat.id)
    if chat_id in clash_lock:
        current_punishment, current_scope = clash_lock[chat_id]
        return await message.reply_text(
            f"⚠️ الكلايش مقفولة بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}\n√"
        )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"cl_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"cl_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"cl_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"**◍ اختر نوع العقوبة لقفل الكلايش ↤︎「 {message.from_user.mention} 」\n√**",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^cl_(mute|restrict|ban)_(\d+)$"))
async def choose_clash_scope(client, callback_query):
    action, user_id = callback_query.data.split('_')[1:]
    user_id = int(user_id)
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ هذا الأمر ليس لك!", show_alert=True)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_cl_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_cl_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^confirm_cl_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_clash_lock(client, callback_query):
    action, scope, user_id = callback_query.data.split('_')[2:]
    user_id = int(user_id)
    chat_id = str(callback_query.message.chat.id)
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ هذا الأمر ليس لك!", show_alert=True)
    clash_lock[chat_id] = [action, scope]
    locks["clash_lock"] = clash_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الكليشة بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}\n√"
    )

@Client.on_message(filters.command(["فتح الكلايش"], "") & filters.group, group=20002)
async def unlock_clash(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in clash_lock:
        return await message.reply_text("**◍ الكلايش غير مقفولة\n√**")
    del clash_lock[chat_id]
    locks["clash_lock"] = clash_lock
    save_locks_chat(locks)
    await message.reply_text(f"**◍ تم فتح الكلايش بواسطة ↤︎「 {message.from_user.mention} 」\n√**")

@Client.on_message(filters.text & filters.group, group=20003)
async def handle_clash_violation(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in clash_lock or len(message.text) < 300:
        return
    OWNER_ID = await get_dev(client.me.username)
    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status == ChatMemberStatus.OWNER or message.from_user.id in [OWNER_ID, OWNER_ID, OWNER_ID] or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    punishment, scope = clash_lock[chat_id]
    if scope == "members" and user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return
    try:
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"**◍ {message.from_user.mention} تم كتمك لإرسال الكلايش طويلة\n√**")
        elif punishment == "restrict":
            await message.reply_text(f"**◍ {message.from_user.mention} يمنع إرسال الكلايش الطويلة هنا\n√**")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"**◍ {message.from_user.mention} تم طردك لإرسال الكلايش طويلة\n√**")
    except Exception as e:
        pass

# قفل المنشن
@Client.on_message(filters.command(["قفل المنشن"], "") & filters.group, group=1212474000)
async def lock_mention(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in mentionn:
        current_punishment, current_scope = mentionn[chat_id]
        await message.reply_text(
            f"⚠️ المنشن مقفول بالفعل\n"
            f"◍ العقوبة الحالية: {current_punishment}\n"
            f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"mention_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"mention_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"mention_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل المنشن ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^mention_(mute|restrict|ban)_(\d+)$"))
async def choose_mention_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_mention_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_mention_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع بما فيهم المشرفين\n"
        "- باستثناء المشرفين: تطبق على الأعضاء العاديين فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_mention_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_mention_punishment(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    mentionn[chat_id] = [action, scope]
    locks["mentionn"] = mentionn
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل المنشن بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط (استثناء المشرفين)'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح المنشن"], "") & filters.group, group=1210002474)
async def unlock_mention(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in mentionn:
        await message.reply_text("⚠️ المنشن غير مقفول بالفعل!")
        return
    del mentionn[chat_id]
    locks["mentionn"] = mentionn
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح المنشن بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.text & filters.group, group=59)
async def handle_mention(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in mentionn:
        return
    if "@" not in message.text:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = mentionn[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ تم كتم {message.from_user.mention} لإرسال منشن ممنوع")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال منشن")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ تم طرد {message.from_user.mention} لإرسال منشن ممنوع")
    except Exception as e:
        print(f"Error handling mention: {e}")

# قفل الفيديو
@Client.on_message(filters.command(["قفل الفيديو"], "") & filters.group, group=1212474487878)
async def lock_video(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in videoo:
        current_punishment, current_scope = videoo[chat_id]
        await message.reply_text(
            f"⚠️ الفيديو مقفول بالفعل\n"
            f"◍ العقوبة الحالية: {current_punishment}\n"
            f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"video_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"video_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"video_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الفيديو ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^video_(mute|restrict|ban)_(\d+)$"))
async def choose_video_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_video_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_video_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_video_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_video_punishment(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    videoo[chat_id] = [action, scope]
    locks["videoo"] = videoo
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الفيديو بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح الفيديو"], "") & filters.group, group=12231212474)
async def unlock_video(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in videoo:
        await message.reply_text("⚠️ الفيديو غير مقفول!")
        return
    del videoo[chat_id]
    locks["videoo"] = videoo
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح الفيديو بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.video & filters.group, group=121247487994)
async def handle_video(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in videoo:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = videoo[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب إرسال فيديو محظور.")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال فيديو")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب إرسال فيديو محظور.")
    except Exception as e:
        print(f"Error handling video: {e}")

# قفل التوجيه
@Client.on_message(filters.command(["قفل التوجيه"], "") & filters.group, group=12124747988)
async def lock_forward(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in tawgeh:
        current_punishment, current_scope = tawgeh[chat_id]
        await message.reply_text(
            f"⚠️ التوجيه مقفول بالفعل\n"
            f"◍ العقوبة الحالية: {current_punishment}\n"
            f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"fw_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"fw_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"fw_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل التوجيه ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^fw_(mute|restrict|ban)_(\d+)$"))
async def choose_forward_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_fw_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_fw_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_fw_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_forward_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    tawgeh[chat_id] = [action, scope]
    locks["tawgeh"] = tawgeh
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل التوجيه بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح التوجيه"], "") & filters.group, group=12124743147)
async def unlock_forward(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in tawgeh:
        await message.reply_text("⚠️ التوجيه غير مقفول!")
        return
    del tawgeh[chat_id]
    locks["tawgeh"] = tawgeh
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح التوجيه بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.forwarded & filters.group, group=1277712474)
async def handle_forwarded(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in tawgeh:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = tawgeh[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب إرسال توجيه محظور.")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال توجيه")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب إرسال توجيه محظور.")
    except Exception as e:
        print(f"Error handling forwarded message: {e}")

# قفل الملصقات
@Client.on_message(filters.command(["قفل الملصقات"], "") & filters.group, group=129797912474)
async def lock_stickers(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in sticker_lock:
        current_punishment, current_scope = sticker_lock[chat_id]
        await message.reply_text(
            f"⚠️ الملصقات مقفولة بالفعل\n"
            f"◍ العقوبة الحالية: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"st_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"st_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"st_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الملصقات ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^st_(mute|restrict|ban)_(\d+)$"))
async def choose_sticker_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_st_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_st_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_st_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_sticker_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    sticker_lock[chat_id] = [action, scope]
    locks["sticker_lock"] = sticker_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الملصقات بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح الملصقات"], "") & filters.group, group=12127989474)
async def unlock_stickers(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in sticker_lock:
        await message.reply_text("⚠️ الملصقات غير مقفولة!")
        return
    del sticker_lock[chat_id]
    locks["sticker_lock"] = sticker_lock
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح الملصقات بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.sticker & filters.group, group=1211112474)
async def handle_sticker(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in sticker_lock:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = sticker_lock[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب إرسال ملصقات.")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال ملصقات")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب إرسال ملصقات.")
    except Exception as e:
        print(f"Error handling sticker: {e}")

# قفل الصور
@Client.on_message(filters.command(["قفل الصور"], "") & filters.group, group=1211472)
async def lock_photos(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in photo_lock:
        current_punishment, current_scope = photo_lock[chat_id]
        await message.reply_text(
            f"⚠️ الصور مقفولة بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"ph_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"ph_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"ph_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الصور ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^ph_(mute|restrict|ban)_(\d+)$"))
async def choose_photo_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_ph_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_ph_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_ph_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_photo_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    photo_lock[chat_id] = [action, scope]
    locks["photo_lock"] = photo_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الصور بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح الصور"], "") & filters.group, group=1212474777)
async def unlock_photos(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in photo_lock:
        await message.reply_text("⚠️ الصور غير مقفولة!")
        return
    del photo_lock[chat_id]
    locks["photo_lock"] = photo_lock
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح الصور بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.photo & filters.group, group=121452474)
async def handle_photo_violation(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in photo_lock:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = photo_lock[chat_id]
        if scope == "members":
            user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
            if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب إرسال صورة محظورة.")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال صورة")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب إرسال صورة محظورة.")
    except Exception as e:
        print(f"Error handling photo violation: {e}")

# قفل الانجليزي
def is_english_only(text):
    return bool(re.fullmatch(r"[A-Za-z\s,!?@#$%^&]+", text.strip()))

@Client.on_message(filters.command(["قفل الانجليزي"], "") & filters.group, group=1000181)
async def lock_english(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر")
    chat_id = str(message.chat.id)
    if chat_id in english_lock:
        current_punishment, current_scope = english_lock[chat_id]
        return await message.reply_text(
            f"⚠️ اللغة الإنجليزية مقفولة بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"en_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"en_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"en_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"**◍ اختر نوع العقوبة لقفل الانجليزي ↤︎「 {message.from_user.mention} 」\n√**",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^en_(mute|restrict|ban)_(\d+)$"))
async def choose_english_scope(client, callback_query):
    action, user_id = callback_query.data.split('_')[1:]
    user_id = int(user_id)
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ هذا الأمر ليس لك!", show_alert=True)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_en_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_en_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^confirm_en_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_english_lock(client, callback_query):
    action, scope, user_id = callback_query.data.split('_')[2:]
    user_id = int(user_id)
    chat_id = str(callback_query.message.chat.id)
    if callback_query.from_user.id != user_id:
        return await callback_query.answer("❌ هذا الأمر ليس لك!", show_alert=True)
    english_lock[chat_id] = [action, scope]
    locks["english_lock"] = english_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل اللغة الإنجليزية بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )

@Client.on_message(filters.command(["فتح الانجليزي"], "") & filters.group, group=100802)
async def unlock_english(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر")
    chat_id = str(message.chat.id)
    if chat_id not in english_lock:
        return await message.reply_text("⚠️ اللغة الإنجليزية غير مقفولة!")
    del english_lock[chat_id]
    locks["english_lock"] = english_lock
    save_locks_chat(locks)
    await message.reply_text(f"**◍ تم فتح الانجليزي بواسطة ↤︎「 {message.from_user.mention} 」\n√**")

@Client.on_message(filters.text & filters.group, group=100013)
async def handle_english_violation(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in english_lock or not is_english_only(message.text):
        return
    OWNER_ID = await get_dev(client.me.username)
    user = await client.get_chat_member(chat_id, message.from_user.id)
    if user.status == ChatMemberStatus.OWNER or message.from_user.id in [OWNER_ID, OWNER_ID, OWNER_ID] or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    punishment, scope = english_lock[chat_id]
    if scope == "members" and user.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return
    try:
        await message.delete()
        if punishment == "mute":
            if chat_id not in muted_users:
                muted_users[chat_id] = []
            if message.from_user.id not in muted_users[chat_id]:
                muted_users[chat_id].append(message.from_user.id)
                locks["muted_users"] = muted_users
                save_locks_chat(locks)
                await message.reply_text(f"**◍ {message.from_user.mention} تم كتمك لاستخدام الإنجليزية فقط \n√**")
        elif punishment == "restrict":
            await message.reply_text(f"**◍ {message.from_user.mention} اللغة الإنجليزية غير مسموح بها هنا \n√**")
        elif punishment == "ban":
            await client.ban_chat_member(message.chat.id, message.from_user.id)
            await message.reply_text(f"**◍ {message.from_user.mention} تم طردك لاستخدام الإنجليزية فقط \n√**")
    except Exception as e:
        pass

# قفل الروابط
@Client.on_message(filters.command(["قفل الروابط"], "") & filters.group, group=110111)
async def lock_links(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in link_lock:
        current_punishment, current_scope = link_lock[chat_id]
        await message.reply_text(
            f"⚠️ الروابط مقفولة بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"ln_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"ln_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"ln_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الروابط ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^ln_(mute|restrict|ban)_(\d+)$"))
async def choose_link_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_ln_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_ln_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_ln_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_link_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    link_lock[chat_id] = [action, scope]
    locks["link_lock"] = link_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الروابط بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح الروابط"], "") & filters.group, group=110222)
async def unlock_links(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in link_lock:
        await message.reply_text("⚠️ الروابط غير مقفولة!")
        return
    del link_lock[chat_id]
    locks["link_lock"] = link_lock
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح الروابط بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.text & filters.group, group=110333)
async def handle_link_violation(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in link_lock:
        return
    if any(link in message.text.lower() for link in ["http://", "https://", "www.", ".com", ".net", ".org", "t.me", "telegram.me"]):
        OWNER_ID = await get_dev(client.me.username)
        if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
            return
        target_member = await client.get_chat_member(chat_id, message.from_user.id)
        if target_member.status == ChatMemberStatus.OWNER:
            return
        try:
            punishment, scope = link_lock[chat_id]
            if scope == "members":
                user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
                if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    return
            await message.delete()
            if punishment == "mute":
                if chat_id not in muted_users:
                    muted_users[chat_id] = []
                if message.from_user.id not in muted_users[chat_id]:
                    muted_users[chat_id].append(message.from_user.id)
                    locks["muted_users"] = muted_users
                    save_locks_chat(locks)
                    await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب إرسال رابط محظور.")
            elif punishment == "restrict":
                await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال رابط")
            elif punishment == "ban":
                await client.ban_chat_member(message.chat.id, message.from_user.id)
                await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب إرسال رابط محظور.")
        except Exception as e:
            print(f"Error handling link violation: {e}")

# الحماية الشاملة (قفل الكل)
@Client.on_message(filters.command(["قفل الحمايه", "قفل الكل"], "") & filters.group, group=18798)
async def lock_protection(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"pr_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"pr_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"pr_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الحماية الشاملة ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^pr_(mute|restrict|ban)_(\d+)$"))
async def choose_protection_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"full_pr_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"full_pr_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق الحماية الشاملة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^full_pr_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_full_protection(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    locks_to_update = {
        "mutaharek": [action, scope],
        "channel_lock": [action, scope],
        "photo_lock": [action, scope],
        "videoo": [action, scope],
        "link_lock": [action, scope],
        "sticker_lock": [action, scope],
        "swear_lock": [action, scope],
        "mentionn": [action, scope],
        "tawgeh": [action, scope]
    }
    for lock_name, lock_value in locks_to_update.items():
        locks[lock_name][chat_id] = lock_value
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم تفعيل الحماية الشاملة بنجاح\n\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}\n\n"
        f"◍ أنواع المحتوى المقفولة:\n"
        f"- السب والشتائم\n"
        f"- الروابط\n"
        f"- الرسائل من القنوات\n"
        f"- الصور\n"
        f"- الفيديوهات\n"
        f"- الملصقات\n"
        f"- التاغ والمنشن\n"
        f"- التوجيهات"
    )
    await callback_query.answer("✓ تم تفعيل الحماية الشاملة", show_alert=True)

@Client.on_message(filters.command(["فتح الحمايه", "فتح الكل"], "") & filters.group, group=545177)
async def unlock_protection(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    locks_to_remove = [
        "mentionn", "mutaharek", "channel_lock",
        "photo_lock", "videoo", "sticker_lock",
        "link_lock", "swear_lock", "tawgeh"
    ]
    for lock_name in locks_to_remove:
        if chat_id in locks[lock_name]:
            try:
                del locks[lock_name][chat_id]
            except Exception:
                pass
    save_locks_chat(locks)
    await message.reply_text(
        f"◍ تم فتح الحماية الشاملة بنجاح\n"
        f"◍ بواسطة ↤︎「 {message.from_user.mention} 」\n\n"
        f"◍ أنواع المحتوى المفتوحة الآن:\n"
        f"- السب والشتائم\n"
        f"- الروابط\n"
        f"- الرسائل من القنوات\n"
        f"- الصور\n"
        f"- الفيديوهات\n"
        f"- الملصقات\n"
        f"- التاغ والمنشن\n"
        f"- التوجيهات"
    )

# قفل الاباحي
@Client.on_message(filters.command(["قفل الاباحى", "قفل الاباحي"], "") & filters.group, group=180148798)
async def lock_pepahyn(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"apr_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"apr_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"apr_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل الاباحي ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^apr_(mute|restrict|ban)_(\d+)$"))
async def choose_proten_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"dfull_pr_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"fdull_pr_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق الحماية ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^dfull_pr_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_fullection(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    locks_to_update = {
        "mutaharek": [action, scope],
        "channel_lock": [action, scope],
        "photo_lock": [action, scope],
        "videoo": [action, scope],
        "link_lock": [action, scope],
        "sticker_lock": [action, scope],
        "swear_lock": [action, scope]
    }
    for lock_name, lock_value in locks_to_update.items():
        locks[lock_name][chat_id] = lock_value
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل الاباحي بنجاح\n\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}\n\n"
        f"◍ أنواع المحتوى المقفولة:\n"
        f"- السب والشتائم\n"
        f"- الروابط\n"
        f"- الرسائل من القنوات\n"
        f"- الصور\n"
        f"- الفيديوهات\n"
        f"- الملصقات"
    )
    await callback_query.answer("✓ تم قفل الاباحي", show_alert=True)

@Client.on_message(filters.command(["فتح الاباحى", "فتح الاباحي"], "") & filters.group, group=5451725787)
async def unlprotection(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    locks_to_remove = [
        "mutaharek", "channel_lock",
        "photo_lock", "videoo", "sticker_lock",
        "link_lock", "swear_lock"
    ]
    for lock_name in locks_to_remove:
        if chat_id in locks[lock_name]:
            try:
                del locks[lock_name][chat_id]
            except Exception:
                pass
    save_locks_chat(locks)
    await message.reply_text(
        f"◍ تم فتح الاباحى بنجاح\n"
        f"◍ بواسطة ↤︎「 {message.from_user.mention} 」\n\n"
        f"◍ أنواع المحتوى المفتوحة الآن:\n"
        f"- السب والشتائم\n"
        f"- الروابط\n"
        f"- الرسائل من القنوات\n"
        f"- الصور\n"
        f"- الفيديوهات\n"
        f"- الملصقات"
    )

# قفل السب
swear_words = [
    "كسمك", "متناك", "احا", "متناكه", "شرموطه", "شمال", 
    "زب", "خول", "قحبه", "عرص", "معرص", "نيك", "متناك",
    "خخخ", "خخ", "خخخخ", "عير", "كحبه", "منيوك"
]

@Client.on_message(filters.command(["قفل السب"], "") & filters.group, group=15989789)
async def lock_swearing(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in swear_lock:
        current_punishment, current_scope = swear_lock[chat_id]
        await message.reply_text(
            f"⚠️ السب مقفل بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"sw_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"sw_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"sw_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل السب ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^sw_(mute|restrict|ban)_(\d+)$"))
async def choose_swear_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_sw_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_sw_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_sw_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_swear_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    swear_lock[chat_id] = [action, scope]
    locks["swear_lock"] = swear_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل السب بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح السب"], "") & filters.group, group=1212474)
async def unlock_swearing(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in swear_lock:
        await message.reply_text("⚠️ السب غير مقفل!")
        return
    del swear_lock[chat_id]
    locks["swear_lock"] = swear_lock
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح السب بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.text & filters.group, group=56)
async def handle_swear_violation(client, message):
    if not message.from_user:
        return
    chat_id = str(message.chat.id)
    if chat_id not in swear_lock:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id)
    if target_member.status == ChatMemberStatus.OWNER:
        return
    message_text = message.text.lower()
    if any(swear_word in message_text for swear_word in swear_words):
        try:
            punishment, scope = swear_lock[chat_id]
            if scope == "members":
                user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
                if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    return
            await message.delete()
            if punishment == "mute":
                if chat_id not in muted_users:
                    muted_users[chat_id] = []
                if message.from_user.id not in muted_users[chat_id]:
                    muted_users[chat_id].append(message.from_user.id)
                    locks["muted_users"] = muted_users
                    save_locks_chat(locks)
                    await message.reply_text(f"◍ {message.from_user.mention} تم كتمك بسبب السب!")
            elif punishment == "restrict":
                await message.reply_text(f"◍ عزيزي {message.from_user.mention} ممنوع ارسال السب")
            elif punishment == "ban":
                await client.ban_chat_member(message.chat.id, message.from_user.id)
                await message.reply_text(f"◍ {message.from_user.mention} تم طردك بسبب السب!")
        except Exception as e:
            print(f"Error handling swear violation: {e}")

# قفل القنوات
@Client.on_message(filters.command(["قفل القنوات"], "") & filters.group, group=1578878)
async def lock_channels(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in channel_lock:
        current_punishment, current_scope = channel_lock[chat_id]
        await message.reply_text(
            f"⚠️ القنوات مقفولة بالفعل\n"
            f"◍ العقوبة: {current_punishment}\n"
            f"◍ النطاق: {'الكل' if current_scope == 'all' else 'الأعضاء فقط'}"
        )
        return
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("مسح", callback_data=f"ch_restrict_{message.from_user.id}")],
        [InlineKeyboardButton("كتم", callback_data=f"ch_mute_{message.from_user.id}")],
        [InlineKeyboardButton("طرد", callback_data=f"ch_ban_{message.from_user.id}")]
    ])
    await message.reply_text(
        f"◍ اختر نوع العقوبة لقفل القنوات ↤︎「 {message.from_user.mention} 」",
        reply_markup=keyboard
    )

@Client.on_callback_query(filters.regex(r"^ch_(mute|restrict|ban)_(\d+)$"))
async def choose_channel_scope(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = int(callback_query.data.split('_')[2])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action = callback_query.data.split('_')[1]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("كل الأعضاء", callback_data=f"confirm_ch_{action}_all_{user_id}")],
        [InlineKeyboardButton("باستثناء المشرفين", callback_data=f"confirm_ch_{action}_members_{user_id}")]
    ])
    await callback_query.message.edit_text(
        f"◍ اختر نطاق العقوبة ({action}):\n"
        "- كل الأعضاء: تطبق على الجميع\n"
        "- باستثناء المشرفين: تطبق على الأعضاء فقط",
        reply_markup=keyboard
    )
    await callback_query.answer()

@Client.on_callback_query(filters.regex(r"^confirm_ch_(mute|restrict|ban)_(all|members)_(\d+)$"))
async def confirm_channel_lock(client, callback_query):
    chat_id = str(callback_query.message.chat.id)
    user_id = int(callback_query.data.split('_')[4])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("هذا الأمر ليس لك!", show_alert=True)
        return
    action, scope = callback_query.data.split('_')[2], callback_query.data.split('_')[3]
    channel_lock[chat_id] = [action, scope]
    locks["channel_lock"] = channel_lock
    save_locks_chat(locks)
    await callback_query.message.edit_text(
        f"◍ تم قفل القنوات بنجاح\n"
        f"◍ العقوبة: {action}\n"
        f"◍ النطاق: {'الكل (بما فيهم المشرفين)' if scope == 'all' else 'الأعضاء فقط'}"
    )
    await callback_query.answer()

@Client.on_message(filters.command(["فتح القنوات"], "") & filters.group, group=87874)
async def unlock_channels(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id not in channel_lock:
        await message.reply_text("⚠️ القنوات غير مقفولة!")
        return
    del channel_lock[chat_id]
    locks["channel_lock"] = channel_lock
    save_locks_chat(locks)
    await message.reply_text(f"◍ تم فتح القنوات بواسطة ↤︎「 {message.from_user.mention} 」")

@Client.on_message(filters.text & filters.group, group=5621175)
async def handle_channel_violation(client, message):
    if not message.sender_chat:
        return
    chat_id = str(message.chat.id)
    if chat_id not in channel_lock:
        return
    OWNER_ID = await get_dev(client.me.username)
    if message.from_user and (message.from_user.id in (OWNER_ID, OWNER_ID, OWNER_ID) or is_main_developer(message.from_user.id) or is_sub_developer(message.from_user.id)):
        return
    target_member = await client.get_chat_member(chat_id, message.from_user.id) if message.from_user else None
    if target_member and target_member.status == ChatMemberStatus.OWNER:
        return
    try:
        punishment, scope = channel_lock[chat_id]
        if scope == "members":
            if message.from_user:
                user_status = await client.get_chat_member(message.chat.id, message.from_user.id)
                if user_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    return
        await message.delete()
        if punishment == "mute":
            if message.from_user:
                if chat_id not in muted_users:
                    muted_users[chat_id] = []
                if message.from_user.id not in muted_users[chat_id]:
                    muted_users[chat_id].append(message.from_user.id)
                    locks["muted_users"] = muted_users
                    save_locks_chat(locks)
                    await message.reply_text(f"◍ {message.sender_chat.title}، تم كتم القناة بسبب الإرسال هنا!")
        elif punishment == "restrict":
            await message.reply_text(f"◍ عزيزي {message.from_user.mention if message.from_user else 'المستخدم'} ممنوع ارسال بواسطة القناة")
        elif punishment == "ban":
            if message.from_user:
                await client.ban_chat_member(message.chat.id, message.from_user.id)
                await message.reply_text(f"◍ {message.sender_chat.title}، تم حظر القناة من المجموعة!")
    except Exception as e:
        print(f"Error handling channel violation: {e}")

# ======================== قائمة الحماية ========================
LOCK_NAMES = {
    'dardasha': 'الدارشة',
    'mutaharek': 'المتحركات',
    'videoo': 'الفيديو',
    'mentionn': 'المنشن',
    'tawgeh': 'التوجيه',
    'channel_lock': 'القنوات',
    'link_lock': 'الروابط',
    'photo_lock': 'الصور',
    'sticker_lock': 'الملصقات',
    'swear_lock': 'السب'
}

@Client.on_message(filters.command(["حماية", "الحمايه", "الحماية"], "") & filters.group, group=5451)
async def protection_menu(client, message):
    if not await check_permission(client, message):
        return await message.reply_text("**◍ تحتاج إلى رتبة مشرف أو أعلى لاستخدام هذا الأمر\n√**")
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("إعدادات الحماية", callback_data=f"hemm {message.from_user.id}")],
        [InlineKeyboardButton("إغلاق", callback_data=f"close {message.from_user.id}")]
    ])
    chat_info = f"""
    **الإعــدادات**

    ◍ المجموعة: {message.chat.title}
    ◍ ايدي المجموعة: `{message.chat.id}`
    ◍ معرف المجموعة: @{message.chat.username if message.chat.username else 'لا يوجد'}

    اختر ما تريد من الخيارات أدناه:
    """
    await message.reply_text(chat_info, reply_markup=keyboard)

@Client.on_callback_query(filters.regex("^hemm (\\d+)$"))
async def protection_settings(client, q: CallbackQuery):
    try:
        user_id = int(q.matches[0].group(1))
        if user_id != q.from_user.id:
            return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
        buttons = []
        for lock_id, lock_name in LOCK_NAMES.items():
            lock_var = globals().get(lock_id, {})
            chat_id = str(q.message.chat.id)
            status = "✓" if chat_id in lock_var else "✗"
            if chat_id in lock_var:
                punishment, scope = lock_var[chat_id]
                btn_text = f"{lock_name} ({punishment}) {status}"
                callback_data = f"unlock_{lock_id}_{user_id}"
            else:
                btn_text = f"{lock_name} {status}"
                callback_data = f"lock_{lock_id}_{user_id}"
            buttons.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])
        buttons.append([InlineKeyboardButton("↩️ رجوع", callback_data=f"back_main_{user_id}")])
        await q.message.edit_text(
            "**إعدادات الحماية:**\n\n"
            "◍ ✓ تعني أن الحماية مفعلة\n"
            "◍ ✗ تعني أن الحماية غير مفعلة\n\n"
            "اختر نوع الحماية الذي تريد تعديله:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    except Exception as e:
        print(f"Error in protection_settings: {str(e)}")
        await q.answer("حدث خطأ أثناء تحميل الإعدادات", show_alert=True)

@Client.on_callback_query(filters.regex("^lock_(\\w+)_(\\d+)$"))
async def lock_item_menu(client, q: CallbackQuery):
    try:
        lock_id = q.matches[0].group(1)
        user_id = int(q.matches[0].group(2))
        if user_id != q.from_user.id:
            return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
        lock_name = LOCK_NAMES.get(lock_id, lock_id)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("مسح", callback_data=f"set_restrict_{lock_id}_{user_id}")],
            [InlineKeyboardButton("كتم", callback_data=f"set_mute_{lock_id}_{user_id}")],
            [InlineKeyboardButton("طرد", callback_data=f"set_ban_{lock_id}_{user_id}")],
            [InlineKeyboardButton("↩️ رجوع", callback_data=f"hemm {user_id}")]
        ])
        await q.message.edit_text(
            f"**إعدادات قفل {lock_name}:**\n\n"
            "اختر طريقة العقاب المطلوبة:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error in lock_item_menu: {str(e)}")
        await q.answer("حدث خطأ أثناء تحميل الخيارات", show_alert=True)

@Client.on_callback_query(filters.regex("^unlock_(\\w+)_(\\d+)$"))
async def unlock_item(client, q: CallbackQuery):
    try:
        lock_id = q.matches[0].group(1)
        user_id = int(q.matches[0].group(2))
        chat_id = str(q.message.chat.id)
        if user_id != q.from_user.id:
            return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
        lock_var = globals().get(lock_id)
        if lock_var is None:
            return await q.answer("⚠️ نوع الحماية غير معروف!", show_alert=True)
        if chat_id in lock_var:
            del lock_var[chat_id]
            save_locks_chat(locks)
        await q.answer(f"✓ تم فتح {LOCK_NAMES.get(lock_id, lock_id)}", show_alert=True)
        await protection_settings(client, q)
    except Exception as e:
        print(f"Error in unlock_item: {str(e)}")
        await q.answer("حدث خطأ أثناء فتح الحماية", show_alert=True)

@Client.on_callback_query(filters.regex("^set_(mute|restrict|ban)_(\\w+)_(\\d+)$"))
async def set_punishment(client, q: CallbackQuery):
    try:
        punishment = q.matches[0].group(1)
        lock_id = q.matches[0].group(2)
        user_id = int(q.matches[0].group(3))
        if user_id != q.from_user.id:
            return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
        lock_var = globals().get(lock_id)
        if lock_var is None:
            return await q.answer("⚠️ نوع الحماية غير معروف!", show_alert=True)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("الكل (بما فيهم المشرفين)", callback_data=f"confirm_{lock_id}_{punishment}_all_{user_id}")],
            [InlineKeyboardButton("الأعضاء فقط", callback_data=f"confirm_{lock_id}_{punishment}_members_{user_id}")],
            [InlineKeyboardButton("↩️ رجوع", callback_data=f"lock_{lock_id}_{user_id}")]
        ])
        await q.message.edit_text(
            f"**اختر نطاق تطبيق العقوبة:**\n\n"
            f"◍ العقوبة: {punishment}\n"
            f"◍ النوع: {LOCK_NAMES.get(lock_id, lock_id)}\n\n"
            "اختر نطاق العقوبة:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error in set_punishment: {str(e)}")
        await q.answer("حدث خطأ أثناء تعيين العقوبة", show_alert=True)

@Client.on_callback_query(filters.regex("^confirm_(\\w+)_(mute|restrict|ban)_(all|members)_(\\d+)$"))
async def confirm_lock_settings(client, q: CallbackQuery):
    try:
        lock_id = q.matches[0].group(1)
        punishment = q.matches[0].group(2)
        scope = q.matches[0].group(3)
        user_id = int(q.matches[0].group(4))
        chat_id = str(q.message.chat.id)
        if user_id != q.from_user.id:
            return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
        lock_var = globals().get(lock_id)
        if lock_var is None:
            return await q.answer("⚠️ نوع الحماية غير معروف!", show_alert=True)
        lock_var[chat_id] = [punishment, scope]
        locks[lock_id] = lock_var
        save_locks_chat(locks)
        await q.answer(f"✓ تم قفل {LOCK_NAMES.get(lock_id, lock_id)}", show_alert=True)
        await protection_settings(client, q)
    except Exception as e:
        print(f"Error in confirm_lock_settings: {str(e)}")
        await q.answer("حدث خطأ أثناء تأكيد القفل", show_alert=True)

@Client.on_callback_query(filters.regex(r"^back_main_(\d+)$"))
async def back_to_main(client, q: CallbackQuery):
    user_id = int(q.matches[0].group(1))
    if user_id != q.from_user.id:
        return await q.answer("⚠️ ليس لديك الصلاحية!", show_alert=True)
    await q.message.delete()
    await protection_menu(client, q.message)
    await q.answer()

# ======================== أوامر الرتب (رفع وتنزيل) ========================
# تم نقل جميع أوامر الرتب من ratab.py كما هي، مع إضافة دالة get_bot_owner
async def get_bot_owner(client):
    bot_username = client.me.username
    return await get_dev(bot_username)

# رفع ادمن
@Client.on_message(filters.command(["رفع ادمن"], "") & filters.group, group=1519957)
async def promote_bot_admin(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة منشئ على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_group_admin(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} ادمن بنجاح🛡\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} هو بالفعل ادمن في هذه المجموعة!")

@Client.on_message(filters.command(["تنزيل ادمن"], "") & filters.group, group=15153457)
async def demote_bot_admin(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة منشئ على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    remove_group_admin(str(message.chat.id), user.id)
    await message.reply(f"**◍ تم تنزيل العضو {user.mention} من الادمنية بنجاح🛡\n√**")

@Client.on_message(filters.command(["الادمنيه", "الادمنية"], "") & filters.group, group=4566153457)
async def list_bot_admins(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    admins = get_group_admins(str(message.chat.id))
    if not admins:
        await message.reply("❌ لا يوجد أدمنية للبوت في هذه المجموعة!")
        return
    text = "🛡 قائمة أدمنية البوت في هذه المجموعة:\n\n"
    for i, admin_id in enumerate(admins, start=1):
        try:
            user = await client.get_users(admin_id)
            text += f"{i}- @{user.username}\n"
        except:
            text += f"{i}- `{admin_id}`\n"
    await message.reply(text)

@Client.on_message(filters.command(["تنزيل الادمنية", "مسح الادمنية", "مسح الادمنيه", "تنزيل الادمنيه"], "") & filters.group, group=4444445)
async def delete_all_bot_admins(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة منشئ على الأقل لإستخدام الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in ranks_data["group_admins"]:
        del ranks_data["group_admins"][chat_id]
        save_ranks(ranks_data)
        await message.reply(f"**◍ تم حذف جميع الادمنيه\n√**")
    else:
        await message.reply("**◍ لا يوجد ادمنيه فى المجموعة\n√**")

# رفع/تنزيل منشئ
@Client.on_message(filters.command(["رفع منشئ"], "") & filters.group, group=1519958)
async def promote_creator(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_group_creator(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} منشئ بنجاح 🛠\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} هو بالفعل منشئ في هذه المجموعة!")

@Client.on_message(filters.command(["تنزيل منشئ"], "") & filters.group, group=15153458)
async def demote_creator(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if remove_group_creator(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم تنزيل العضو {user.mention} من المنشئين بنجاح 🛠\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} ليس منشئاً في هذه المجموعة!")

@Client.on_message(filters.command(["المنشئين", "المشئين"], "") & filters.group, group=4566153458)
async def list_creators(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    creators = get_group_creators(str(message.chat.id))
    if not creators:
        await message.reply("❌ لا يوجد منشئين للبوت في هذه المجموعة!")
        return
    text = "🛠 قائمة منشئي البوت في هذه المجموعة:\n\n"
    for creator_id in creators:
        try:
            user = await client.get_users(creator_id)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{creator_id}`\n"
    await message.reply(text)

@Client.on_message(filters.command(["مسح المنشئين", "حذف المنشئين", "تنزيل المنشئين"], "") & filters.group, group=8888888)
async def delete_all_creators(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in ranks_data["group_creators"]:
        del ranks_data["group_creators"][chat_id]
        save_ranks(ranks_data)
        await message.reply(f"**◍ تم حذف جميع المنشئين\n√**")
    else:
        await message.reply("**◍ لا يوجد منشئين فى المجموعة\n√**")

# رفع/تنزيل مالك
@Client.on_message(filters.command(["رفع مالك"], "") & filters.group, group=1111111)
async def promote_owner(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_group_owner(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} مالك بنجاح 👑\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} هو بالفعل مالك في هذه المجموعة!")

@Client.on_message(filters.command(["تنزيل مالك"], "") & filters.group, group=2222222)
async def demote_owner(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if remove_group_owner(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم تنزيل العضو {user.mention} من المالكين بنجاح 👑\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} ليس مالكاً في هذه المجموعة!")

@Client.on_message(filters.command(["المالكين", "الملاك"], "") & filters.group, group=3333333)
async def list_owners(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    owners = get_group_owners(str(message.chat.id))
    if not owners:
        await message.reply("❌ لا يوجد ملاك للبوت في هذه المجموعة!")
        return
    text = "👑 قائمة المالكين في هذه المجموعة:\n\n"
    for owner_id in owners:
        try:
            user = await client.get_users(owner_id)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{owner_id}`\n"
    await message.reply(text)

@Client.on_message(filters.command(["تنزيل المالكين", "مسح المالكين"], "") & filters.group, group=4444444)
async def delete_all_owners(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    chat_id = str(message.chat.id)
    owners = get_group_owners(chat_id)
    if len(owners) <= 1:
        return await message.reply("**◍ لا يوجد مالكين إضافيين للحذف\n√**")
    owners_to_delete = owners[1:]
    deleted = 0
    for oid in owners_to_delete:
        if remove_group_owner(chat_id, oid):
            deleted += 1
    await message.reply(f"**◍ تم حذف {deleted} من المالكين بنجاح\n√**")

# رفع/تنزيل مميز
@Client.on_message(filters.command(["رفع مميز"], "") & filters.group, group=5555555)
async def promote_vip(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة ادمن على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_group_vip(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} مميز بنجاح 🌟\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} هو بالفعل مميز في هذه المجموعة!")

@Client.on_message(filters.command(["تنزيل مميز"], "") & filters.group, group=66616666)
async def demote_vip(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة ادمن على الأقل لإستخدام الأمر\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if remove_group_vip(str(message.chat.id), user.id):
        await message.reply(f"**◍ تم تنزيل العضو {user.mention} من المميزين بنجاح 🌟\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} ليس مميزاً في هذه المجموعة!")

@Client.on_message(filters.command(["المميزين"], "") & filters.group, group=77777077)
async def list_vips(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    vips = get_group_vips(str(message.chat.id))
    if not vips:
        await message.reply("❌ لا يوجد مميزين في هذه المجموعة!")
        return
    text = "🌟 قائمة المميزين في هذه المجموعة:\n\n"
    for vip_id in vips:
        try:
            user = await client.get_users(vip_id)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{vip_id}`\n"
    await message.reply(text)

@Client.on_message(filters.command(["مسح المميزين", "تنزيل المميزين"], "") & filters.group, group=88888818)
async def delete_all_vips(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة ادمن على الأقل لإستخدام الأمر\n√**")
    chat_id = str(message.chat.id)
    if chat_id in ranks_data["group_vips"]:
        del ranks_data["group_vips"][chat_id]
        save_ranks(ranks_data)
        await message.reply(f"**◍ تم حذف جميع المميزين\n√**")
    else:
        await message.reply("**◍ لا يوجد مميزين فى المجموعة\n√**")

# رفع/تنزيل مطور أساسي
@Client.on_message(filters.command(["رفع مطور اساسي"], "") & filters.group, group=8888818)
async def promote_main_dev(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    if user_id not in [OWNER_ID, OWNER_ID, OWNER_ID]:
        return await message.reply_text("**◍ هذا الامر خاص بالمطور فقط\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_main_developer(user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} مطور اساسي بنجاح 👨🏻‍💻\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} مطور أساسي بالفعل.")

@Client.on_message(filters.command(["تنزيل مطور اساسي"], "") & filters.group, group=8818)
async def demote_main_dev(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    if user_id not in [OWNER_ID, OWNER_ID, OWNER_ID]:
        return await message.reply_text("**◍ هذا الامر خاص بالمطور فقط\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if remove_main_developer(user.id):
        await message.reply(f"**◍ تم تنزيل العضو {user.mention} من المطورين الاساسين بنجاح 👨🏻‍💻\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} ليس مطورًا أساسيًا.")

@Client.on_message(filters.command(["المطورين"], ""), group=8814818)
async def list_main_devs(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    devs = get_main_developers()
    if not devs:
        return await message.reply("**❌ لا يوجد مطورين أساسيين**")
    text = "**👨🏻‍💻 قائمة المطورين الأساسيين:**\n\n"
    for uid in devs:
        try:
            user = await client.get_users(uid)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{uid}`\n"
    await message.reply(text)

@Client.on_message(filters.command(["مسح المطورين الاساسين", "تنزيل المطورين الاساسين"], "") & filters.group, group=88810818)
async def delete_all_main_devs(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    if user_id not in [OWNER_ID, OWNER_ID, OWNER_ID]:
        return await message.reply_text("**◍ تحتاج إلى مالك البوت على الأقل لإستخدام الأمر\n√**")
    ranks_data["main_developers"] = []
    save_ranks(ranks_data)
    await message.reply(f"**◍ تم حذف جميع المطورين الاساسين\n√**")

# رفع/تنزيل مطور ثانوي
@Client.on_message(filters.command(["رفع مطور ثانوي"], "") & filters.group, group=8898718)
async def promote_sub_dev(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_main_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ هذا الامر خاص بالمطور والمطور الاساسى فقط\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if add_sub_developer(user.id):
        await message.reply(f"**◍ تم رفع العضو {user.mention} مطور ثانوي بنجاح 🕵🏻‍♂️\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} مطور ثانوي بالفعل.")

@Client.on_message(filters.command(["تنزيل مطور ثانوي"], "") & filters.group, group=108818)
async def demote_sub_dev(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_main_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ هذا الامر خاص بالمطور والمطور الاساسى فقط\n√**")
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) > 2:
        target = message.text.split(maxsplit=2)[2]
        if target.startswith("@"):
            try:
                user = await client.get_users(target.strip("@"))
            except:
                return await message.reply_text("❌ لا يمكن العثور على المستخدم")
        elif target.isdigit():
            try:
                user = await client.get_users(int(target))
            except:
                return await message.reply_text("❌ رقم ID غير صحيح")
        else:
            return await message.reply_text("⚠️ يرجى إرسال معرف المستخدم أو الرد على رسالته")
    else:
        ask = await zom_ask(client, message, "**◍ أرسل الآن آيدي المستخدم\n√**")
        if not ask:
            return
        try:
            user = await client.get_users(ask.text)
        except:
            return await message.reply_text("❌ رقم ID غير صحيح")
    if remove_sub_developer(user.id):
        await message.reply(f"**◍ تم تنزيل العضو {user.mention} من المطورين الثانويين بنجاح 🕵🏻‍♂️\n√**")
    else:
        await message.reply(f"⚠️ {user.mention} ليس مطورًا ثانويًا.")

@Client.on_message(filters.command(["المطورين الثانويين"], ""), group=888854818)
async def list_sub_devs(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_creator(str(message.chat.id), user_id),
        is_group_admin(str(message.chat.id), user_id),
        is_group_vip(str(message.chat.id), user_id),
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مميز على الأقل لإستخدام الأمر\n√**")
    devs = get_sub_developers()
    if not devs:
        return await message.reply("**❌ لا يوجد مطورين ثانويين**")
    text = "**🕵🏻‍♂️ قائمة المطورين الثانويين:**\n\n"
    for uid in devs:
        try:
            user = await client.get_users(uid)
            text += f"- {user.mention}\n"
        except:
            text += f"- `{uid}`\n"
    await message.reply(text)

# مسح جميع الرتب
@Client.on_message(filters.command(["مسح الرتب", "تنزيل الرتب", "تنزيل جميع الرتب"], "") & filters.group, group=8888802488)
async def delete_all_ranks(client, message):
    OWNER_ID = await get_bot_owner(client)
    user_id = message.from_user.id
    allowed = any([
        is_group_owner(str(message.chat.id), user_id),
        is_main_developer(user_id),
        is_sub_developer(user_id),
        user_id in [OWNER_ID, OWNER_ID, OWNER_ID],
    ])
    if not allowed:
        return await message.reply_text("**◍ تحتاج إلى رتبة مالك على الأقل لإستخدام الأمر\n√**")
    chat_id = str(message.chat.id)
    ranks_data["group_creators"].pop(chat_id, None)
    ranks_data["group_admins"].pop(chat_id, None)
    ranks_data["group_vips"].pop(chat_id, None)
    owners = ranks_data["group_owners"].get(chat_id, [])
    if len(owners) > 1:
        ranks_data["group_owners"][chat_id] = owners[:1]
    save_ranks(ranks_data)
    await message.reply("**◍ تم حذف جميع الرتب\n√**")

# ======================== معالج الردود ========================
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