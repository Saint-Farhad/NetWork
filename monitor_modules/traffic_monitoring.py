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

def get_interface_list():
    """دریافت لیست اینترفیس‌ها"""
    interfaces = list(psutil.net_io_counters(pernic=True).keys())
    interfaces.append("Return to main menu")  # اضافه کردن گزینه بازگشت
    return interfaces

def select_interface(stdscr):
    """نمایش لیست اینترفیس‌ها برای انتخاب توسط کاربر"""
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
            if current_idx == len(interfaces) - 1:
                return None  # بازگشت به منوی اصلی
            return interfaces[current_idx]
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, iface in enumerate(interfaces):
                x = width // 2 - len(iface) // 2
                y = height // 2 - len(interfaces) // 2 + idx
                if my == y and x <= mx <= x + len(iface):
                    current_idx = idx
                    if current_idx == len(interfaces) - 1:
                        return None
                    return interfaces[current_idx]

def monitor_traffic(stdscr, interface):
    """نمایش ترافیک ورودی و خروجی به صورت لحظه‌ای"""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # تنظیمات جدول
    col_widths = [20, 20, 20, 20]  # عرض ستون‌ها: Bytes In, Bytes Out, Packets In, Packets Out
    start_y = 4
    start_x = (width - sum(col_widths)) // 2

    # تنظیم کردن nodelay برای پذیرش کلید بدون توقف در هر حلقه
    stdscr.nodelay(True)
    while True:
        traffic_info = psutil.net_io_counters(pernic=True).get(interface)
        if not traffic_info:
            stdscr.addstr(1, 0, "Error: Interface not found.")
            stdscr.refresh()
            time.sleep(2)
            break

        # ساختار جدول و عنوان
        title = f"Traffic Monitoring for Interface: {interface}"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)
        
        # نمایش عنوان ستون‌ها
        headers = ["Bytes In", "Bytes Out", "Packets In", "Packets Out"]
        for i, header in enumerate(headers):
            stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)
        
        # کشیدن کادر برای جدول
        draw_box(stdscr, start_y - 1, start_x - 1, sum(col_widths) + len(headers) - 1, 4)
        
        # نمایش اطلاعات ترافیک در جدول
        stdscr.addstr(start_y + 1, start_x, f"{traffic_info.bytes_recv:<20}")
        stdscr.addstr(start_y + 1, start_x + col_widths[0], f"{traffic_info.bytes_sent:<20}")
        stdscr.addstr(start_y + 1, start_x + col_widths[0] + col_widths[1], f"{traffic_info.packets_recv:<20}")
        stdscr.addstr(start_y + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2], f"{traffic_info.packets_sent:<20}")
        
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

def show_traffic_monitoring(stdscr):
    """نمایش نظارت بر ترافیک"""
    selected_interface = select_interface(stdscr)
    if selected_interface:
        monitor_traffic(stdscr, selected_interface)
