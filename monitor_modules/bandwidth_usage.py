import curses
import psutil
import time
import subprocess
import logging

# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='bandwidth_monitor.log', level=logging.INFO,
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
    """دریافت لیست اینترفیس‌های شبکه با استفاده از دستور سیستم."""
    interfaces = subprocess.check_output("ls /sys/class/net", shell=True).decode().splitlines()
    interfaces.append("All Interfaces")  # اضافه کردن گزینه "تمام اینترفیس‌ها"
    interfaces.append("Return to main menu")  # اضافه کردن گزینه "بازگشت"
    return interfaces

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
            logging.info(f"Interface selected: {selected_iface}")
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
                    logging.info(f"Interface selected via mouse: {selected_iface}")
                    current_idx = idx
                    if current_idx == len(interfaces) - 1:
                        return None
                    return selected_iface

def get_bandwidth(interface):
    """دریافت میزان پهنای باند ورودی و خروجی هر اینترفیس با استفاده از psutil."""
    net_io = psutil.net_io_counters(pernic=True)

    if interface == "All Interfaces":
        total_inbound = sum(iface.bytes_recv for iface in net_io.values())
        total_outbound = sum(iface.bytes_sent for iface in net_io.values())
    else:
        iface_stats = net_io.get(interface)
        if iface_stats:
            total_inbound = iface_stats.bytes_recv
            total_outbound = iface_stats.bytes_sent
        else:
            logging.warning(f"Interface {interface} not found.")
            total_inbound = total_outbound = 0
    
    return total_inbound, total_outbound

def format_speed(bytes_value, time_interval):
    """فرمت کردن سرعت پهنای باند به Mbps."""
    speed_bps = (bytes_value * 8) / time_interval  # تبدیل بایت به بیت
    speed_mbps = speed_bps / (1024 * 1024)  # تبدیل بیت بر ثانیه به مگابیت بر ثانیه
    return speed_mbps

def draw_bandwidth_graph(stdscr, label, current_speed, max_width, start_y, start_x):
    """رسم گراف پهنای باند با استفاده از کاراکترهای متنی."""
    current_speed_mbps = float(current_speed)  # تبدیل رشته به عدد
    graph_width = int((current_speed_mbps / 100) * max_width)  # تبدیل سرعت به درصدی از عرض جدول
    graph = f"[{'=' * graph_width}{' ' * (max_width - graph_width)}]"  # ساخت گراف با کاراکتر '='

    stdscr.addstr(start_y, start_x, f"{label}: {graph} {current_speed_mbps:.2f} Mbps")

def monitor_bandwidth(stdscr, interface):
    """نمایش پهنای باند به صورت لحظه‌ای."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # تنظیمات جدول
    max_graph_width = 25  # حداکثر عرض گراف متنی
    start_y = 4
    start_x = (width - max_graph_width - 30) // 2  # تنظیم جدول در مرکز

    stdscr.nodelay(True)  # تنظیم برای پذیرش ورودی کلید بدون توقف

    prev_inbound, prev_outbound = get_bandwidth(interface)

    while True:
        # گرفتن پهنای باند فعلی
        time.sleep(1)  # تأخیر یک ثانیه‌ای برای محاسبه سرعت
        curr_inbound, curr_outbound = get_bandwidth(interface)

        inbound_speed = format_speed(curr_inbound - prev_inbound, 1)
        outbound_speed = format_speed(curr_outbound - prev_outbound, 1)

        # به‌روزرسانی برای دفعه بعد
        prev_inbound, prev_outbound = curr_inbound, curr_outbound

        # ساختار جدول و عنوان
        title = f"Real-Time Bandwidth Usage for Interface: {interface}"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # کشیدن کادر برای جدول
        draw_box(stdscr, start_y - 1, start_x - 2, max_graph_width + 30, 6)

        # رسم گراف پهنای باند
        draw_bandwidth_graph(stdscr, "Inbound", inbound_speed, max_graph_width, start_y + 1, start_x)
        draw_bandwidth_graph(stdscr, "Outbound", outbound_speed, max_graph_width, start_y + 3, start_x)

        # اضافه کردن پیام خروج
        message = "Press any key to return to the menu..."
        stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)

        # به‌روزرسانی صفحه
        stdscr.refresh()

        # بررسی اینکه آیا کلیدی فشرده شده است یا خیر
        key = stdscr.getch()
        if key != -1:
            logging.info(f"Exiting bandwidth monitoring for interface: {interface}")
            stdscr.nodelay(False)  # بازگرداندن حالت عادی ترمینال قبل از خروج
            break

def show_bandwidth_usage(stdscr):
    """نمایش نظارت بر پهنای باند."""
    selected_interface = select_interface(stdscr)
    if selected_interface:
        monitor_bandwidth(stdscr, selected_interface)
