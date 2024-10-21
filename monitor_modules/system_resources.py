import curses
import psutil
import time

def draw_box(stdscr, y, x, width, height):
    """تابعی برای کشیدن کادر دور یک بخش"""
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

def get_system_resources():
    """دریافت اطلاعات منابع سیستم (CPU، RAM، دیسک)"""
    cpu_usage = psutil.cpu_percent(interval=1)
    cpu_cores = psutil.cpu_count(logical=True)
    memory_info = psutil.virtual_memory()
    disk_usage = psutil.disk_usage('/')

    resources = {
        "CPU Cores": f"{cpu_cores}",
        "CPU Usage (%)": f"{cpu_usage}%",
        "Total Memory (GB)": f"{memory_info.total / (1024 ** 3):.2f} GB",
        "Used Memory (GB)": f"{memory_info.used / (1024 ** 3):.2f} GB",
        "Available Memory (GB)": f"{memory_info.available / (1024 ** 3):.2f} GB",
        "Memory Usage (%)": f"{memory_info.percent}%",
        "Total Disk Space (GB)": f"{disk_usage.total / (1024 ** 3):.2f} GB",
        "Used Disk Space (GB)": f"{disk_usage.used / (1024 ** 3):.2f} GB",
        "Free Disk Space (GB)": f"{disk_usage.free / (1024 ** 3):.2f} GB",
        "Disk Usage (%)": f"{disk_usage.percent}%",
    }
    return resources

def show_system_resources(stdscr):
    """نمایش منابع سیستم در جدول به صورت real-time"""
    curses.curs_set(0)  # مخفی کردن نشانگر
    stdscr.nodelay(True)  # تنظیم برای نادیده گرفتن کلیدها (برای آپدیت real-time)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # دریافت اطلاعات منابع سیستم
        resources = get_system_resources()

        # تنظیمات جدول
        col_widths = [30, 40]  # عرض ستون‌ها: Metric، Value (افزایش فاصله بین ستون‌ها)
        table_width = sum(col_widths) + 4
        start_y = 4
        start_x = (width - table_width) // 2

        # نمایش عنوان جدول
        title = "Real-time System Resources"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش عنوان ستون‌ها
        headers = ["Metric", "Value"]
        for i, header in enumerate(headers):
            stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)

        # کشیدن کادر برای جدول
        draw_box(stdscr, start_y - 1, start_x - 2, table_width, len(resources) + 3)

        # نمایش اطلاعات در جدول
        for i, (metric, value) in enumerate(resources.items()):
            stdscr.addstr(start_y + i + 1, start_x, metric)
            stdscr.addstr(start_y + i + 1, start_x + col_widths[0], value)

        # نمایش پیام خروج در انتهای صفحه
        message = "Press 'q' to return to the menu..."
        stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)

        stdscr.refresh()

        # بررسی اینکه آیا کاربر کلید 'q' را زده است برای خروج
        key = stdscr.getch()
        if key == ord('q'):
            stdscr.nodelay(False)  # غیرفعال کردن حالت non-blocking
            break

        # تأخیر کوتاه برای آپدیت real-time
        time.sleep(1)
