import curses
from network_config import network_config_menu  # فراخوانی منوی Network Configuration
from firewall_config import firewall_config_menu  # فراخوانی منوی Firewall Management
from vSwitch_config import manage_vs_main_menu  # فراخوانی منوی Open vSwitch Management
from network_monitor import network_monitor_menu  # فراخوانی منوی Network Monitoring

# لیست گزینه‌های منو
menu_items = [
    "1- Linux Network Configuration",
    "2- Firewall Management",
    "3- Open vSwitch Management",
    "4- Network Monitoring",
    "5- About this Project",
    "6- Exit"
]

def handle_menu_selection(stdscr, current_idx):
    """
    بررسی انتخاب کاربر و اجرای عملکرد مربوطه

    پارامترها:
    stdscr -- پنجره ترمینال curses
    current_idx -- شاخص آیتم انتخابی در منو
    """
    if current_idx == 0:
        network_config_menu(stdscr)  # فراخوانی منوی Linux Network Configuration
    elif current_idx == 1:
        firewall_config_menu(stdscr)  # فراخوانی منوی مدیریت فایروال
    elif current_idx == 2:
        manage_vs_main_menu(stdscr)  # فراخوانی منوی مدیریت Open vSwitch
    elif current_idx == 3:
        network_monitor_menu(stdscr)  # فراخوانی منوی Network Monitoring
    elif current_idx == 4:
        display_about_project(stdscr)  # نمایش اطلاعات مربوط به پروژه
    elif current_idx == 5:
        confirm_exit(stdscr)  # نمایش پیغام تأیید برای خروج از برنامه

def confirm_exit(stdscr):
    """
    نمایش پیام تأیید خروج از برنامه
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    message = "Are you sure you want to exit? (y/n)"
    stdscr.addstr(height // 2, width // 2 - len(message) // 2, message)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord('y') or key == ord('Y'):
            exit(0)  # خروج از برنامه
        elif key == ord('n') or key == ord('N'):
            return  # بازگشت به منوی اصلی

def display_about_project(stdscr):
    """
    نمایش اطلاعات در مورد پروژه

    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    message = (
        "Network Configuration and Firewall Management Project\n"
        "Created by: Farhad Shafiei\n"
        "Version: 1.0.7\n"
        "This project allows users to manage network settings, firewalls, Open vSwitch, "
        "and monitor network traffic via a TUI interface."
    )
    for idx, line in enumerate(message.split("\n")):
        stdscr.addstr(height // 2 - len(message.split("\n")) // 2 + idx, width // 2 - len(line) // 2, line)
    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()

def draw_menu(stdscr):
    """
    رسم منوی اصلی و مدیریت ورودی‌ها

    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    # فعال کردن پشتیبانی از ماوس
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    # شاخص گزینه فعلی
    current_idx = 0

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # رسم آیتم‌های منو
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب‌شده با نمایش معکوس
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        # دریافت ورودی
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            handle_menu_selection(stdscr, current_idx)
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()

            # چک کردن کلیک ماوس روی آیتم‌های منو
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    handle_menu_selection(stdscr, current_idx)
                    break

if __name__ == "__main__":
    curses.wrapper(draw_menu)
