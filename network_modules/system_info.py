import curses
import subprocess
import re

def draw_box(stdscr, y, x, width, height):
    """
    تابعی برای کشیدن کادر در اطراف یک بخش.
    
    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    y -- مختصات y شروع کادر
    x -- مختصات x شروع کادر
    width -- عرض کادر
    height -- ارتفاع کادر
    """
    # کشیدن گوشه‌های کادر
    stdscr.addch(y, x, curses.ACS_ULCORNER)
    stdscr.addch(y, x + width - 1, curses.ACS_URCORNER)
    stdscr.addch(y + height - 1, x, curses.ACS_LLCORNER)
    stdscr.addch(y + height - 1, x + width - 1, curses.ACS_LRCORNER)
    
    # کشیدن خطوط افقی و عمودی کادر
    for i in range(1, width - 1):
        stdscr.addch(y, x + i, curses.ACS_HLINE)
        stdscr.addch(y + height - 1, x + i, curses.ACS_HLINE)
    
    for i in range(1, height - 1):
        stdscr.addch(y + i, x, curses.ACS_VLINE)
        stdscr.addch(y + i, x + width - 1, curses.ACS_VLINE)

def parse_network_info():
    """
    پردازش اطلاعات شبکه و بازگرداندن لیستی از اینترفیس‌ها و آدرس‌های IP.
    
    برمی‌گرداند:
    لیستی از اینترفیس‌ها شامل وضعیت، آدرس IPv4 و IPv6.
    """
    # اجرای دستور ip برای دریافت اطلاعات شبکه
    ip_output = subprocess.check_output("ip -br a", shell=True).decode()
    interfaces = []
    
    # پردازش هر خط از خروجی
    for line in ip_output.splitlines():
        parts = re.split(r'\s+', line)
        if len(parts) >= 3:
            iface = parts[0]  # نام اینترفیس
            status = parts[1]  # وضعیت اینترفیس
            ip_addrs = parts[2:]  # لیست آدرس‌های IP
            ipv4_addr = next((ip for ip in ip_addrs if ":" not in ip), "N/A")  # دریافت آدرس IPv4
            ipv6_addr = next((ip for ip in ip_addrs if ":" in ip), "N/A")  # دریافت آدرس IPv6
            interfaces.append((iface, status, ipv4_addr, ipv6_addr))  # اضافه کردن به لیست اینترفیس‌ها
    
    return interfaces

def get_current_dns():
    """
    دریافت DNS سرورهای فعلی.
    
    برمی‌گرداند:
    لیستی از DNS سرورهای فعلی.
    """
    # اجرای دستور resolvectl برای دریافت وضعیت DNS
    dns_output = subprocess.check_output("resolvectl status", shell=True).decode()
    dns_lines = dns_output.splitlines()
    dns_servers = []

    # جستجوی خطوط شامل "DNS Servers"
    for line in dns_lines:
        if "DNS Servers" in line:
            dns = line.split("DNS Servers:")[1].strip()
            dns_servers.append(dns)
    
    # در صورتی که DNS سروری یافت نشد، "N/A" برگردانده می‌شود
    return dns_servers if dns_servers else ["N/A"]

def system_info(stdscr):
    """
    نمایش اطلاعات شبکه شامل اینترفیس‌ها و DNS سرورها.
    
    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    title = "Network Interface Information"
    
    # نمایش عنوان در مرکز صفحه
    stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)
    
    # دریافت اطلاعات شبکه و DNS
    interfaces = parse_network_info()
    dns_servers = get_current_dns()
    
    # تنظیم عرض ستون‌ها برای جدول
    col_widths = [15, 10, 20, 30]  # عرض ستون‌ها: اینترفیس، وضعیت، IPv4، IPv6
    start_y = 4
    start_x = (width - sum(col_widths)) // 2
    
    # نمایش عنوان ستون‌ها
    headers = ["Interface", "Status", "IPv4 Address", "IPv6 Address"]
    for i, header in enumerate(headers):
        stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)
    
    # کشیدن کادر دور جدول
    draw_box(stdscr, start_y - 1, start_x - 1, sum(col_widths) + len(headers) - 1, len(interfaces) + 3)
    
    # نمایش اطلاعات اینترفیس‌ها
    for i, (iface, status, ipv4_addr, ipv6_addr) in enumerate(interfaces):
        stdscr.addstr(start_y + i + 1, start_x, iface)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0], status)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1], ipv4_addr)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2], ipv6_addr)
    
    # نمایش DNS های فعلی
    dns_start_y = start_y + len(interfaces) + 3
    dns_title = "Current DNS Servers:"
    stdscr.addstr(dns_start_y, width // 2 - len(dns_title) // 2, dns_title, curses.A_BOLD | curses.A_UNDERLINE)
    
    for i, dns in enumerate(dns_servers):
        stdscr.addstr(dns_start_y + i + 1, width // 2 - len(dns) // 2, dns)
    
    # نمایش پیام بازگشت در انتهای صفحه
    message = "Press any key to return to the menu..."
    stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)
    
    stdscr.refresh()
    stdscr.getch()
