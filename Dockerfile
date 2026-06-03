FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# نصب ابزارهای مورد نیاز سیستم‌عامل (اختیاری اما برای کامپایل برخی کتابخانه‌ها لازم است)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# کپی و نصب کتابخانه‌های پایتون
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# کپی کردن کل کدهای پروژه به کانتینر
COPY . /app/

# 🌟 ساخت پوشه رسانه (media) برای فایل‌های ورد و تنظیم دسترسی کامل دیتابیس SQLite
RUN mkdir -p /app/media && chmod -R 777 /app

# 🌟 باز کردن پورت ۸۰۰۰ داکر
EXPOSE 8000

# 🌟 دستور نهایی برای اعمال مایگریشن‌ها و روشن شدن سرور جنگو
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]