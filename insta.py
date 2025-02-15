import requests
import uuid
import os
from pyrogram import Client, filters

# Created By @ImSoheilOfficial
api_id ="21294482"  # api_id خود را وارد کنید
api_hash = "990ec4db2f39b94eb696f2058369b931"  # api_hash خود را وارد کنید
bot_token ="8034043748:AAF1u8VjlS4uwYTwaBrKgH8vxbGoPXZeGX0"  # توکن ربات خود را وارد کنید

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# تابع برای گرفتن لینک ویدیو از API
def get_video_url(link):
    api_url = f"https://api.silohost.ir/api/api.php?link={link}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == True:
            if data['data'].get('status') == "redirect":
                return data['data'].get('url')
            else:
                print("Unexpected data status:", data['data'].get('status'))
        else:
            print("API request failed:", data.get('message'))
    else:
        print("API request failed with status code:", response.status_code)
    return None


@app.on_message(filters.text)
async def handle_message(client, message):
    link = message.text
    
    # بررسی لینک اینستاگرام
    if link.startswith("https://www.instagram.com") or link.startswith("http://www.instagram.com"):
        reply_message = await message.reply_text("در حال پردازش لینک...\nلطفا منتظر بمانید!", reply_to_message_id=message.id)
        
        # دریافت URL ویدیو
        video_url = get_video_url(link)
        if video_url:
            file_name = f"video_{uuid.uuid4().hex}.mp4"
            
            # دانلود ویدیو با استفاده از requests
            chunk_size = 1024 * 500  # 500KB per chunk
            with requests.get(video_url, stream=True) as r:
                total_size = int(r.headers.get('content-length', 0))
                if total_size == 0:
                    await reply_message.edit_text("مشکلی در دریافت اطلاعات اندازه ویدیو پیش آمده است.")
                    return

                downloaded_size = 0
                with open(file_name, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        done = int(50 * downloaded_size / total_size)  # میزان پیشرفت دانلود
                        if downloaded_size % (500 * 1024) == 0:  # هر نیم مگابایت پیشرفت
                            await reply_message.edit_text(f"در حال دانلود ویدیو... {done}%")
            
            # ارسال ویدیو به تلگرام
            await reply_message.edit_text("دانلود کامل شد. در حال آپلود ویدیو...")
            await client.send_video(chat_id=message.chat.id, video=file_name, reply_to_message_id=message.id)

            # حذف فایل ویدیو بعد از ارسال
            os.remove(file_name)
        else:
            await reply_message.edit_text("مشکلی در دریافت ویدیو از لینک مورد نظر پیش آمده است.")
    
    else:
        pass  # اگر لینک از نوع اینستاگرام نبود، هیچ کاری انجام نمی‌دهیم

if __name__ == "__main__":
    app.run()  # این خط مهم است!

