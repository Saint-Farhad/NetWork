import curses
import subprocess
import time
import psutil  # برای استفاده از psutil برای all interfaces
import logging

# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='protocol_statistics.log', level=logging.INFO,
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
    """دریافت لیست اینترفیس‌ها."""
    try:
        interfaces = subprocess.check_output("ls /sys/class/net", shell=True).decode().splitlines()
        interfaces.append("All Interfaces")  # اضافه کردن گزینه All Interfaces
        interfaces.append("Return to main menu")  # اضافه کردن گزینه بازگشت
        logging.info("Fetched interface list.")
        return interfaces
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching interface list: {str(e)}")
        return []

def get_interface_ip(interface):
    """پیدا کردن آدرس IP اینترفیس."""
    try:
        ip_output = subprocess.check_output(f"ip addr show {interface}", shell=True).decode()
        for line in ip_output.splitlines():
            if "inet " in line:  # پیدا کردن آدرس IPv4
                ip_address = line.strip().split()[1].split('/')[0]
                logging.info(f"IP address for {interface}: {ip_address}")
                return ip_address
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Error fetching IP for {interface}: {str(e)}")
        return None

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

        # نمایش لیست اینترفیس‌ها در مرکز صفحه با شماره‌گذاری
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

def get_protocol_statistics(interface):
    """دریافت آمار پروتکل‌های TCP و UDP با استفاده از ss و netstat."""
    logging.info(f"Fetching protocol statistics for interface: {interface}")
    if interface == "All Interfaces":
        # دریافت آمار کلی از تمام اینترفیس‌ها
        net_io = psutil.net_io_counters()
        tcp_cmd = "ss -t state established | wc -l"
        tcp_connections = int(subprocess.check_output(tcp_cmd, shell=True).decode().strip())
        udp_packets_recv = net_io.packets_recv
        udp_packets_sent = net_io.packets_sent
    else:
        # برای اینترفیس خاص آدرس IP را پیدا کنیم
        ip_address = get_interface_ip(interface)
        if not ip_address:
            logging.warning(f"No IP address found for {interface}")
            tcp_connections = 0
        else:
            # استفاده از آدرس IP برای فیلتر کردن
            tcp_cmd = f"ss -t state established '( src {ip_address} or dst {ip_address} )' | wc -l"
            tcp_connections = int(subprocess.check_output(tcp_cmd, shell=True).decode().strip())

        # دریافت UDP Packets Received و Sent برای اینترفیس خاص
        udp_recv_cmd = f"cat /sys/class/net/{interface}/statistics/rx_packets"
        udp_sent_cmd = f"cat /sys/class/net/{interface}/statistics/tx_packets"
        try:
            udp_packets_recv = int(subprocess.check_output(udp_recv_cmd, shell=True).decode().strip())
            udp_packets_sent = int(subprocess.check_output(udp_sent_cmd, shell=True).decode().strip())
        except subprocess.CalledProcessError as e:
            logging.error(f"Error fetching UDP statistics for {interface}: {str(e)}")
            udp_packets_recv = udp_packets_sent = 0

    logging.info(f"TCP connections: {tcp_connections}, UDP packets received: {udp_packets_recv}, UDP packets sent: {udp_packets_sent}")
    return tcp_connections, udp_packets_recv, udp_packets_sent

def monitor_protocols(stdscr, interface):
    """نمایش آمار پروتکل‌های TCP و UDP به صورت لحظه‌ای."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # تنظیمات جدول
    col_widths = [50, 25]  # افزایش عرض ستون اول به 50 برای فاصله بیشتر
    table_width = sum(col_widths) + 4  # محاسبه عرض کل جدول
    start_y = 4
    start_x = (width - table_width) // 2  # تنظیم جدول در مرکز

    stdscr.nodelay(True)  # تنظیم برای پذیرش ورودی کلید بدون توقف

    while True:
        # دریافت آمار پروتکل‌ها
        tcp_connections, udp_packets_recv, udp_packets_sent = get_protocol_statistics(interface)

        # ساختار جدول و عنوان
        title = f"Protocol Statistics for Interface: {interface}"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)
        
        # کشیدن کادر برای جدول
        draw_box(stdscr, start_y - 1, start_x - 2, table_width, 6)
        
        # نمایش اطلاعات در جدول
        stdscr.addstr(start_y + 1, start_x, "TCP Connections")
        stdscr.addstr(start_y + 1, start_x + col_widths[0], f"{tcp_connections:<25}")
        stdscr.addstr(start_y + 2, start_x, "UDP Packets Received")
        stdscr.addstr(start_y + 2, start_x + col_widths[0], f"{udp_packets_recv:<25}")
        stdscr.addstr(start_y + 3, start_x, "UDP Packets Sent")
        stdscr.addstr(start_y + 3, start_x + col_widths[0], f"{udp_packets_sent:<25}")

        # اضافه کردن پیام خروج
        message = "Press any key to return to the menu..."
        stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)

        # به‌روزرسانی هر ثانیه
        stdscr.refresh()

        # بررسی اینکه آیا کلیدی فشرده شده است یا خیر
        key = stdscr.getch()
        if key != -1:
            stdscr.nodelay(False)  # بازگرداندن حالت عادی ترمینال قبل از خروج
            break

        # تأخیر یک ثانیه‌ای برای به‌روزرسانی اطلاعات
        time.sleep(1)

def show_protocol_statistics(stdscr):
    """نمایش نظارت بر آمار پروتکل‌ها."""
    selected_interface = select_interface(stdscr)
    if selected_interface:
        monitor_protocols(stdscr, selected_interface)
