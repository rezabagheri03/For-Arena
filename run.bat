#!/bin/bash

# اسکریپت راه‌اندازی سریع وبسایت
# Quick Start Script for Resume Website

echo "🚀 در حال راه‌اندازی وبسایت رزومه..."

# بررسی وجود Python
if ! command -v python3 &> /dev/null; then
    echo "❌ خطا: Python3 نصب نیست!"
    exit 1
fi

# بررسی وجود محیط مجازی
if [ ! -d "venv" ]; then
    echo "📦 ایجاد محیط مجازی..."
    python3 -m venv venv
fi

# فعال‌سازی محیط مجازی
echo "🔌 فعال‌سازی محیط مجازی..."
source venv/bin/activate

# نصب وابستگی‌ها
echo "📥 نصب پکیج‌ها..."
pip install -q -r requirements.txt

# اجرای سرور
echo "✅ سرور در حال اجرا روی http://localhost:5000"
echo "برای توقف سرور، Ctrl+C را بزنید"
echo ""
python app.py

