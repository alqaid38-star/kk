import aiohttp
import json
import os

async def edit_colored_keyboard(chat_id, message_id, keyboard_dict, token):
    url = f"https://api.telegram.org/bot{token}/editMessageReplyMarkup"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {
            "inline_keyboard": keyboard_dict
        }
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            try:
                return await resp.json()
            except:
                return await resp.text()

async def send_colored_photo(chat_id, photo, caption, keyboard_dict, token):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    data = aiohttp.FormData()
    data.add_field('chat_id', str(chat_id))
    data.add_field('caption', caption)
    data.add_field('reply_markup', json.dumps({"inline_keyboard": keyboard_dict}))
    data.add_field('parse_mode', 'Markdown')

    if isinstance(photo, str) and (photo.startswith('http') or len(photo) > 100): # URL or likely a file_id
        data.add_field('photo', photo)
    elif os.path.exists(str(photo)): # Local file path
        data.add_field('photo', open(photo, 'rb'))
    else:
        data.add_field('photo', photo) # Fallback (maybe a file_id)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as resp:
            try:
                return await resp.json()
            except:
                return await resp.text()
