#!/bin/bash

# به‌روزرسانی لیست بسته‌ها
echo "Updating system packages..."
sudo apt update

# نصب پکیج‌های سیستمی از جمله psutil
echo "Installing system packages including psutil..."
sudo apt install python3-psutil
sudo apt install -y python3 python3-pip python3-venv git python3-psutil systemd-resolved nftables openvswitch-switch


# تنظیم DNS به صورت خودکار
echo "Setting up DNS..."
sudo bash -c 'echo "nameserver 8.8.8.8" > /etc/resolv.conf'
sudo systemctl restart systemd-resolved

# نصب کتابخانه‌های پایتونی در محیط مجازی (بدون psutil چون از طریق apt نصب شد)
pip install -r requirements.txt

# تنظیمات nftables
echo "Applying nftables rules..."
sudo nft add table inet filter
sudo nft add chain inet filter input { type filter hook input priority 0 \; policy accept \; }
sudo nft add chain inet filter output { type filter hook output priority 0 \; policy accept \; }
sudo nft add chain inet filter forward { type filter hook forward priority 0 \; policy accept \; }
sudo nft add table ip nat
sudo nft add chain ip nat prerouting { type nat hook prerouting priority -100 \; policy accept \; }
sudo nft add chain ip nat postrouting { type nat hook postrouting priority 100 \; policy accept \; }

# راه‌اندازی مجدد systemd-resolved
echo "Restarting systemd-resolved service..."
sudo systemctl restart systemd-resolved

# اجرای برنامه پایتون در محیط مجازی
python3 tui_main.py

# پایان نصب
echo "Installation completed successfully."
