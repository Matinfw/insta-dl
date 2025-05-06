FROM python:3.11-slim

WORKDIR /app

# کپی فایل‌ها به کانتینر
COPY . .

# نصب پکیج‌ها
RUN pip install --no-cache-dir python-telegram-bot yt-dlp requests

# در صورت نیاز می‌تونی این خط رو فعال کنی (مثلاً اگه بات پورت خاصی باز می‌کنه)
# EXPOSE 8000

# اجرای اسکریپت
CMD ["python", "insta.py"]