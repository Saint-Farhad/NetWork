import asyncio
import logging
import psutil
from telegram import Bot

# تنظیمات ربات تلگرام
telegram_api_token = None
telegram_chat_id = None

async def send_telegram_message(token, chat_id, message):
    """ارسال پیام به تلگرام به صورت asynchronous"""
    try:
        bot = Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        logging.error(f"Error in send_telegram_message: {e}")

def telegram_bot_menu():
    """نمایش منوی تنظیمات تلگرام و دریافت API Token و Chat ID"""
    global telegram_api_token, telegram_chat_id

    # دریافت API Token ربات تلگرام
    telegram_api_token = input("لطفاً API Token ربات تلگرام خود را وارد کنید و Enter بزنید: ")

    # دریافت Chat ID صاحب ربات
    telegram_chat_id = input("لطفاً Chat ID خود را وارد کنید و Enter بزنید: ")

    # استفاده از asyncio برای ارسال پیام تست به صورت async
    asyncio.run(test_and_send_message())

def test_telegram_bot(token, chat_id):
    """ارسال پیام تست برای بررسی صحت API و Chat ID"""
    try:
        bot = Bot(token=token)
        bot.send_message(chat_id=chat_id, text="🔔 این یک پیام تست است.")
        return True
    except Exception as e:
        logging.error(f"Error in test_telegram_bot: {e}")
        return False

async def test_and_send_message():
    """ارسال پیام تست برای بررسی صحت و سپس پیام فعالسازی"""
    global telegram_api_token, telegram_chat_id

    if test_telegram_bot(telegram_api_token, telegram_chat_id):
        await send_telegram_message(telegram_api_token, telegram_chat_id, "📡 ربات مانیتورینگ شبکه با موفقیت برای شما فعال شد!")
    else:
        print("⚠️ API Token یا Chat ID نادرست است. لطفاً دوباره تلاش کنید.")

async def monitor_system_resources():
    """بررسی وضعیت منابع سیستم و ارسال هشدار به تلگرام"""
    global telegram_api_token, telegram_chat_id
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_info = psutil.virtual_memory()

    # هشدارهای مربوط به CPU
    if cpu_usage > 80:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"🔥 هشدار حیاتی: مصرف CPU از ۸۰٪ فراتر رفته است ({cpu_usage}%)")
    elif cpu_usage > 60:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"⚠️ هشدار مهم: مصرف CPU از ۶۰٪ فراتر رفته است ({cpu_usage}%)")
    elif cpu_usage > 10:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"🔔 اطلاعیه: مصرف CPU از ۱۰٪ فراتر رفته است ({cpu_usage}%)")

    # هشدارهای مربوط به RAM
    if memory_info.percent > 80:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"🔥 هشدار حیاتی: مصرف RAM از ۸۰٪ فراتر رفته است ({memory_info.percent}%)")
    elif memory_info.percent > 60:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"⚠️ هشدار مهم: مصرف RAM از ۶۰٪ فراتر رفته است ({memory_info.percent}%)")
    elif memory_info.percent > 10:
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"🔔 اطلاعیه: مصرف RAM از ۱۰٪ فراتر رفته است ({memory_info.percent}%)")

async def monitor_interface_state(interfaces):
    """بررسی وضعیت اینترفیس‌ها و ارسال هشدار در صورت تغییر"""
    global telegram_api_token, telegram_chat_id
    for interface in interfaces:
        state = get_interface_state(interface)
        if state == 'down':
            await send_telegram_message(telegram_api_token, telegram_chat_id, f"⚠️ هشدار مهم: اینترفیس {interface} به حالت down تغییر کرده است.")

def get_interface_state(interface):
    """دریافت وضعیت اینترفیس (up/down)"""
    # در اینجا باید یک تابع برای بررسی وضعیت اینترفیس وجود داشته باشد
    return 'up'  # فرضی

async def monitor_network_traffic():
    """بررسی ترافیک شبکه و ارسال هشدار در صورت حجم غیر عادی"""
    # فرض کنید ترافیک شبکه را مانیتور می‌کنید
    traffic_usage = 1000  # میزان ترافیک در MB
    global telegram_api_token, telegram_chat_id
    if traffic_usage > 1000:  # فرض کنید 1000 MB حجم غیر عادی است
        await send_telegram_message(telegram_api_token, telegram_chat_id, f"🔥 هشدار حیاتی: حجم غیر عادی ترافیک شبکه ({traffic_usage} MB)")
