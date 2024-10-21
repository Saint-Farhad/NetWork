#!/bin/bash

# بررسی اینکه آیا آدرس گیت‌هاب به عنوان ورودی دریافت شده است یا خیر
if [ -z "$1" ]; then
    echo "Usage: $0 <https://github.com/Saint-Farhad/Project>"
    exit 1
fi

# کلون کردن مخزن از گیت‌هاب
REPO_URL=$1
echo "Cloning the repository from $REPO_URL ..."
git clone $REPO_URL

# استخراج نام پوشه پروژه از آدرس مخزن
REPO_NAME=$(basename $REPO_URL .git)

# تغییر دایرکتوری به پوشه پروژه
cd $REPO_NAME || { echo "Failed to enter the project directory"; exit 1; }

# بررسی وجود فایل Install.sh
if [ ! -f "Install.sh" ]; then
    echo "Install.sh file not found in the repository!"
    exit 1
fi

# اعطای مجوز اجرایی به Install.sh
chmod +x Install.sh

# اجرای اسکریپت نصب
echo "Running the Install.sh script..."
./Install.sh

# پایان
echo "Installation completed successfully."
