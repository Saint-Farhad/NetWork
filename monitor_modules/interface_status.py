import curses
import psutil
import os
import time
import requests
import logging

# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='interface_status.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def draw_box(stdscr, y, x, width, height):
    """تابعی برای کشیدن کادر دور یک بخش."""
    stdscr.addch(y, x, curses.ACS_ULCORNER)
    stdscr.addch(y, x + width - 1, curses.ACS_URCORNER)
    stdscr.addch(y + height - 1, x, curses.ACS_LLCORNER)
    stdscr.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)
    
    for i in range(1, width - 1):
        stdscr.addch(y, x + i, curses.ACS_HLINE)
        stdscr.addch(y + height - 1, x + i, curses.ACS_HLINE)
    
    for i in range(1, height - 1):
        stdscr.addch(y + i, x, curses.ACS_VLINE)
        stdscr.addch(y + i, x + width - 1, curses.ACS_VLINE)

def get_interface_speed(interface):
    """دریافت سرعت واقعی شبکه با تست دانلود."""
    logging.info(f"Fetching network speed for interface: {interface}")
    return test_network_speed_with_requests()

def test_network_speed_with_requests():
    """تست سرعت شبکه با دانلود یک فایل کوچک."""
    url = "http://speedtest.tele2.net/10MB.zip"  # آدرس فایل تست (10 مگابایت)
    logging.info(f"Starting network speed test with URL: {url}")
    
    try:
        # شروع اندازه‌گیری زمان
        start_time = time.time()

        # دانلود فایل با درخواست GET (تکه تکه برای جلوگیری از مصرف زیاد حافظه)
        response = requests.get(url, stream=True)
        total_downloaded = 0

        # هر چانک را به صورت تکه‌تکه دریافت می‌کنیم
        for chunk in response.iter_content(chunk_size=8192):
            total_downloaded += len(chunk)

        # پایان اندازه‌گیری زمان
        end_time = time.time()

        # محاسبه مدت زمان دانلود
        duration = end_time - start_time

        # محاسبه سرعت دانلود (بیت بر ثانیه)
        speed_bps = (total_downloaded * 8) / duration
        speed_mbps = speed_bps / (1024 * 1024)  # تبدیل به مگابیت بر ثانیه

        logging.info(f"Download completed in {duration:.2f} seconds, Speed: {speed_mbps:.2f} Mbps")
        return f"{speed_mbps:.2f} Mbps"

    except Exception as e:
        logging.error(f"Error during speed test: {str(e)}")
        return f"Error: {str(e)}"

def get_interface_type(interface):
    """تشخیص نوع اینترفیس (فیزیکی یا مجازی)."""
    # بررسی اینکه آیا اینترفیس به یک دستگاه فیزیکی متصل است یا خیر
    device_path = f"/sys/class/net/{interface}/device"
    
    if os.path.exists(device_path):
        logging.info(f"Interface {interface} is Physical")
        return "Physical"  # اگر مسیر device وجود داشت، اینترفیس فیزیکی است
    else:
        logging.info(f"Interface {interface} is Virtual")
        return "Virtual"   # در غیر این صورت، مجازی است

def show_interface_status(stdscr):
    """نمایش وضعیت اینترفیس‌ها در جدول."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    title = "Network Interface Status"
    
    # نمایش عنوان در مرکز صفحه
    stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

    # دریافت اطلاعات اینترفیس‌ها
    interfaces = psutil.net_if_stats()
    logging.info("Fetched network interface stats")

    # تنظیمات جدول (افزایش عرض ستون‌ها برای خوانایی بهتر)
    col_widths = [20, 15, 20, 20]  # عرض ستون‌ها: اینترفیس، وضعیت، نوع، سرعت
    start_y = 4
    start_x = (width - sum(col_widths)) // 2
    
    # نمایش عنوان ستون‌ها
    headers = ["Interface", "Status", "Type", "Speed"]
    for i, header in enumerate(headers):
        stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)
    
    # کشیدن کادر برای جدول
    draw_box(stdscr, start_y - 1, start_x - 1, sum(col_widths) + len(headers) - 1, len(interfaces) + 3)

    # نمایش اطلاعات اینترفیس‌ها در جدول
    for i, (iface_name, iface_info) in enumerate(interfaces.items()):
        status = "UP" if iface_info.isup else "DOWN"
        iface_type = get_interface_type(iface_name)
        speed = get_interface_speed(iface_name) if iface_info.isup else "-"

        # نمایش اطلاعات در جدول
        stdscr.addstr(start_y + i + 1, start_x, iface_name)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0], status)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1], iface_type)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2], speed)
        logging.info(f"Interface: {iface_name}, Status: {status}, Type: {iface_type}, Speed: {speed}")
    
    # نمایش پیام خروج در انتهای صفحه
    message = "Press any key to return to the menu..."
    stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)
    
    stdscr.refresh()
    stdscr.getch()
