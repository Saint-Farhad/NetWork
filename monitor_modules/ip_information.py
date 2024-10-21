import curses
import subprocess
import logging

# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='network_interface.log', level=logging.INFO,
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

def get_interface_list():
    """دریافت لیست اینترفیس‌ها از سیستم."""
    try:
        interfaces = subprocess.check_output("ls /sys/class/net", shell=True).decode().splitlines()
        interfaces.append("Return to main menu")  # اضافه کردن گزینه بازگشت به منوی اصلی
        logging.info("Fetched network interface list")
        return interfaces
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching interface list: {str(e)}")
        return []

def get_ip_addresses(interface):
    """پیدا کردن آدرس‌های IP (IPv4 و IPv6) برای یک اینترفیس مشخص."""
    try:
        ip_output = subprocess.check_output(f"ip addr show {interface}", shell=True).decode()
        ipv4, ipv6 = "N/A", "N/A"
    
        for line in ip_output.splitlines():
            if "inet " in line and "scope global" in line:  # پیدا کردن آدرس IPv4
                ipv4 = line.strip().split()[1].split('/')[0]
            elif "inet6 " in line and "scope global" in line:  # پیدا کردن آدرس IPv6
                ipv6 = line.strip().split()[1].split('/')[0]
        
        logging.info(f"IP addresses for interface {interface}: IPv4: {ipv4}, IPv6: {ipv6}")
        return ipv4, ipv6
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching IP addresses for {interface}: {str(e)}")
        return "N/A", "N/A"

def select_interface(stdscr):
    """نمایش لیست اینترفیس‌ها برای انتخاب توسط کاربر."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    interfaces = get_interface_list()
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        title = "Select Network Interface"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش لیست اینترفیس‌ها در مرکز صفحه
        for idx, iface in enumerate(interfaces):
            label = f"{idx + 1}. {iface}"  # اضافه کردن شماره کنار هر اینترفیس
            x = width // 2 - len(label) // 2
            y = height // 2 - len(interfaces) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, label, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب‌شده
            else:
                stdscr.addstr(y, x, label)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(interfaces)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(interfaces)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            selected_iface = interfaces[current_idx]
            logging.info(f"Selected interface: {selected_iface}")
            if current_idx == len(interfaces) - 1:
                return None  # بازگشت به منوی اصلی
            return selected_iface
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, iface in enumerate(interfaces):
                x = width // 2 - len(iface) // 2
                y = height // 2 - len(interfaces) // 2 + idx
                if my == y and x <= mx <= x + len(iface):
                    selected_iface = interfaces[current_idx]
                    logging.info(f"Selected interface via mouse: {selected_iface}")
                    current_idx = idx
                    if current_idx == len(interfaces) - 1:
                        return None
                    return selected_iface

def show_ip_information(stdscr):
    """نمایش اطلاعات IP مربوط به اینترفیس انتخاب‌شده در جدول."""
    selected_interface = select_interface(stdscr)
    if not selected_interface:
        logging.info("No interface selected, returning to main menu")
        return  # بازگشت به منوی اصلی

    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت آدرس‌های IP مربوط به اینترفیس
    ipv4, ipv6 = get_ip_addresses(selected_interface)

    # تنظیمات جدول
    col_widths = [20, 30, 45]  # عرض ستون‌ها: Interface، IPv4، IPv6
    table_width = sum(col_widths) + 4
    start_y = 4
    start_x = (width - table_width) // 2

    # نمایش عنوان جدول
    title = f"IP Information for Interface: {selected_interface}"
    stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

    # نمایش عنوان ستون‌ها
    headers = ["Interface", "IPv4", "IPv6"]
    for i, header in enumerate(headers):
        stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)

    # کشیدن کادر برای جدول
    draw_box(stdscr, start_y - 1, start_x - 2, table_width, 4)

    # نمایش اطلاعات در جدول
    stdscr.addstr(start_y + 1, start_x, selected_interface)
    stdscr.addstr(start_y + 1, start_x + col_widths[0], ipv4)
    stdscr.addstr(start_y + 1, start_x + col_widths[0] + col_widths[1], ipv6)

    # نمایش پیام خروج در انتهای صفحه
    message = "Press any key to return to the menu..."
    stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)

    stdscr.refresh()
    stdscr.getch()
    logging.info(f"Displayed IP information for {selected_interface}")
