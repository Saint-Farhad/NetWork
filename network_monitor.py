import curses
import logging
from monitor_modules.interface_status import show_interface_status
from monitor_modules.traffic_monitoring import show_traffic_monitoring
from monitor_modules.protocol_statistics import show_protocol_statistics
from monitor_modules.ip_information import show_ip_information
from monitor_modules.bandwidth_usage import show_bandwidth_usage
from monitor_modules.system_resources import show_system_resources


# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='network_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelنامه)s - %(message)s')


def center_text(stdscr, text):
    """نمایش متن در مرکز صفحه."""
    height, width = stdscr.getmaxyx()
    x = width // 2 - len(text) // 2
    y = height // 2
    stdscr.addstr(y, x, text)


def show_telegram_message(stdscr):
    """نمایش پیام در مرکز صفحه برای Telegram Bot Settings."""
    stdscr.clear()
    center_text(stdscr, "This section is under construction and will be released in future updates.")
    stdscr.refresh()
    stdscr.getch()  # منتظر فشردن کلید برای بازگشت به منوی اصلی


def show_system_resource_menu(stdscr):
    """نمایش منوی منابع سرور (رم، سی‌پی‌یو، دیسک)."""
    menu_items = [
        "1- View System Resources",    # نمایش منابع سرور
        "2- Telegram Bot Settings",    # تنظیمات ربات تلگرام
        "3- Return to Network Monitoring"  # بازگشت به منوی نظارت شبکه
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "System Resource Monitoring"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو و بررسی انتخاب‌ها
        for idx, item in enumerate(menu_items):
            row_offset = idx
            if idx == current_idx:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                logging.info("System resources viewed")
                show_system_resources(stdscr)  # نمایش منابع سیستم
            elif current_idx == 1:
                logging.info("Telegram bot settings selected")
                show_telegram_message(stdscr)  # نمایش پیام "در حال ساخت"
            elif current_idx == 2:
                logging.info("Returned to Network Monitoring")
                return  # بازگشت به منوی نظارت شبکه


def network_monitor_menu(stdscr):
    """نمایش منوی اصلی نظارت شبکه."""
    menu_items = [
        "1- Interface Status",           # وضعیت اینترفیس‌ها
        "2- Traffic Monitoring",         # مانیتورینگ ترافیک
        "3- Protocol Statistics",        # آمار پروتکل‌ها
        "4- IP Information",             # اطلاعات IP
        "5- Bandwidth Usage",            # استفاده از پهنای باند
        "6- System Resource Monitoring", # منابع سرور
        "7- Return to main menu"         # بازگشت به منوی اصلی
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = "Network Monitoring"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو و بررسی انتخاب‌ها
        for idx, item in enumerate(menu_items):
            row_offset = idx
            if idx == current_idx:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                logging.info("Interface Status selected")
                show_interface_status(stdscr)
            elif current_idx == 1:
                logging.info("Traffic Monitoring selected")
                show_traffic_monitoring(stdscr)
            elif current_idx == 2:
                logging.info("Protocol Statistics selected")
                show_protocol_statistics(stdscr)
            elif current_idx == 3:
                logging.info("IP Information selected")
                show_ip_information(stdscr)
            elif current_idx == 4:
                logging.info("Bandwidth Usage selected")
                show_bandwidth_usage(stdscr)
            elif current_idx == 5:
                logging.info("System Resource Monitoring menu opened")
                show_system_resource_menu(stdscr)  # اینجا تابع جدید فراخوانی می‌شود
            elif current_idx == 6:
                logging.info("Returned to main menu")
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                row_offset = idx
                item_y = height // 2 + row_offset
                item_x_start = width // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)
                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        logging.info("Interface Status selected via mouse")
                        show_interface_status(stdscr)
                    elif current_idx == 1:
                        logging.info("Traffic Monitoring selected via mouse")
                        show_traffic_monitoring(stdscr)
                    elif current_idx == 2:
                        logging.info("Protocol Statistics selected via mouse")
                        show_protocol_statistics(stdscr)
                    elif current_idx == 3:
                        logging.info("IP Information selected via mouse")
                        show_ip_information(stdscr)
                    elif current_idx == 4:
                        logging.info("Bandwidth Usage selected via mouse")
                        show_bandwidth_usage(stdscr)
                    elif current_idx == 5:
                        logging.info("System Resource Monitoring menu opened via mouse")
                        show_system_resource_menu(stdscr)  # فراخوانی تابع جدید
                    elif current_idx == 6:
                        logging.info("Returned to main menu via mouse")
                        return

if __name__ == "__main__":
    logging.info("Network Monitor started")
    curses.wrapper(network_monitor_menu)
