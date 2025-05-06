
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import yt_dlp
import requests
from urllib.parse import urlparse

# تنظیم لاگینگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات خود را اینجا قرار دهید
TOKEN = 'YOUR_BOT_TOKEN'

def start(update: Update, context: CallbackContext) -> None:
    """دستور شروع"""
    welcome_message = """
    سلام! 👋
    به ربات دانلودر خوش آمدید!
    
    لینک ویدیو را از یکی از پلتفرم‌های زیر ارسال کنید:
    - یوتیوب 🎥
    - اینستاگرام 📸
    - آپارات 🎬
    """
    update.message.reply_text(welcome_message)

def get_platform(url: str) -> str:
    """تشخیص پلتفرم از URL"""
    domain = urlparse(url).netloc
    if 'youtube.com' in domain or 'youtu.be' in domain:
        return 'youtube'
    elif 'instagram.com' in domain:
        return 'instagram'
    elif 'aparat.com' in domain:
        return 'aparat'
    return 'unknown'

def download_video(url: str, platform: str) -> str:
    """دانلود ویدیو"""
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return os.path.join('downloads', f"{info['title']}.{info['ext']}")
    except Exception as e:
        logger.error(f"Error downloading video: {str(e)}")
        return None

def handle_url(update: Update, context: CallbackContext) -> None:
    """پردازش URL های ارسالی"""
    url = update.message.text
    chat_id = update.message.chat_id
    
    # ارسال پیام در حال پردازش
    processing_message = update.message.reply_text("در حال پردازش لینک... ⏳")
    
    platform = get_platform(url)
    if platform == 'unknown':
        processing_message.edit_text("لینک نامعتبر است! ❌")
        return
    
    try:
        # دانلود ویدیو
        video_path = download_video(url, platform)
        
        if video_path and os.path.exists(video_path):
            # ارسال ویدیو
            with open(video_path, 'rb') as video_file:
                context.bot.send_video(
                    chat_id=chat_id,
                    video=video_file,
                    caption=f"دانلود شده از {platform} ✅"
                )
            # پاک کردن فایل
            os.remove(video_path)
            processing_message.delete()
        else:
            processing_message.edit_text("خطا در دانلود ویدیو! ❌")
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        processing_message.edit_text("خطا در پردازش ویدیو! ❌")

def help_command(update: Update, context: CallbackContext) -> None:
    """دستور راهنما"""
    help_text = """
    🔹 راهنمای استفاده از ربات:
    
    1️⃣ لینک ویدیو را کپی کنید
    2️⃣ لینک را برای ربات ارسال کنید
    3️⃣ منتظر دانلود و ارسال ویدیو باشید
    
    🔸 پلتفرم‌های پشتیبانی شده:
    - یوتیوب
    - اینستاگرام
    - آپارات
    
    ⚠️ در صورت بروز مشکل، دوباره تلاش کنید.
    """
    update.message.reply_text(help_text)

def error_handler(update: Update, context: CallbackContext) -> None:
    """مدیریت خطاها"""
    logger.error(f"Error: {context.error}")
    if update:
        update.message.reply_text("خطایی رخ داد! لطفا دوباره تلاش کنید. ❌")

def main() -> None:
    """تابع اصلی ربات"""
    # ایجاد پوشه دانلود‌ها
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    # راه‌اندازی ربات
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # اضافه کردن هندلرها
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_url))
    dispatcher.add_error_handler(error_handler)

    # شروع ربات
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()