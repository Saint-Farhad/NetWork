import subprocess
import curses
import logging

# تنظیمات لاگ‌گذاری
logging.basicConfig(filename='ovs_status.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def draw_box(stdscr, y, x, width, height):
    """
    ترسیم کادری به دور یک بخش مشخص برای نمایش اطلاعات در رابط کاربری متنی (TUI).
    """
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

def get_ovs_info():
    """
    دریافت اطلاعات از Open vSwitch شامل بریج‌ها، پورت‌ها، VLAN‌ها، وضعیت ترانک/اکسس، آدرس IP و وضعیت پورت.
    """
    try:
        # دریافت لیست بریج‌ها از OVS
        bridges_output = subprocess.check_output("ovs-vsctl list-br", shell=True).decode().splitlines()
        ovs_info = []

        for bridge in bridges_output:
            # دریافت لیست پورت‌های مرتبط با بریج
            ports_output = subprocess.check_output(f"ovs-vsctl list-ports {bridge}", shell=True).decode().splitlines()

            for port in ports_output:
                vlan_mode = get_vlan_mode(port)
                ip_address = get_interface_ip(port)
                port_status = get_port_status(port)

                # تشخیص اینکه پورت مربوط به VLAN است یا خیر
                if '.' in port:
                    vlan_id = port.split('.')[-1]  # استخراج VLAN ID
                    ovs_info.append((bridge, port.split('.')[0], vlan_id, vlan_mode, port_status, ip_address))
                else:
                    # پورت‌هایی که به VLAN متصل نیستند
                    ovs_info.append((bridge, port, "N/A", vlan_mode, port_status, ip_address))

        logging.info("Successfully retrieved OVS info.")
        return ovs_info
    except subprocess.CalledProcessError:
        logging.error("Failed to retrieve OVS info.")
        return []

def get_vlan_mode(port):
    """
    دریافت وضعیت VLAN پورت و تشخیص اینکه آیا پورت در حالت Trunk یا Access است.
    """
    try:
        vlan_mode_output = subprocess.check_output(f"ovs-vsctl get port {port} vlan_mode", shell=True).decode().strip()
        if vlan_mode_output == "trunk":
            return {"Trunk": "Yes", "Access": "No"}  # پورت در حالت ترانک
        elif vlan_mode_output == "access":
            return {"Trunk": "No", "Access": "Yes"}  # پورت در حالت اکسس
        return {"Trunk": "No", "Access": "No"}  # هیچ حالتی ندارد
    except subprocess.CalledProcessError:
        logging.error(f"Failed to retrieve VLAN mode for port {port}.")
        return {"Trunk": "Unknown", "Access": "Unknown"}

def get_interface_ip(interface):
    """
    دریافت آدرس IP اینترفیس مرتبط با پورت.
    """
    try:
        ip_output = subprocess.check_output(f"ip -br addr show {interface}", shell=True).decode().strip()
        if ip_output:
            parts = ip_output.split()
            if len(parts) > 2:
                return parts[2]  # آدرس IP
        return "N/A"
    except subprocess.CalledProcessError:
        logging.error(f"Failed to retrieve IP address for interface {interface}.")
        return "N/A"

def get_port_status(port):
    """
    دریافت وضعیت فعال یا غیرفعال بودن پورت.
    """
    try:
        status_output = subprocess.check_output(f"ip link show {port}", shell=True).decode().strip()
        if "UP" in status_output:
            return "Enabled"
        return "Disabled"
    except subprocess.CalledProcessError:
        logging.error(f"Failed to retrieve port status for {port}.")
        return "Unknown"

def show_ovs_status(stdscr):
    """
    نمایش وضعیت Open vSwitch شامل اطلاعات بریج‌ها، پورت‌ها، VLANها، ترانک، Access، IP و وضعیت پورت.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    title = "OVS Status"

    # نمایش عنوان در مرکز صفحه
    stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

    # دریافت اطلاعات OVS
    ovs_info = get_ovs_info()

    if not ovs_info:
        stdscr.addstr(height // 2, width // 2 - len("Failed to retrieve OVS information.") // 2, "Failed to retrieve OVS information.", curses.A_BOLD | curses.A_BLINK)
        stdscr.refresh()
        stdscr.getch()
        return

    # تنظیمات جدول برای نمایش اطلاعات
    col_widths = [15, 15, 10, 10, 10, 15, 25]
    start_y = 4
    start_x = (width - sum(col_widths)) // 2

    # نمایش عنوان ستون‌ها
    headers = ["Bridge", "Port", "VLAN", "Trunk", "Access", "Port Status", "IP"]
    for i, header in enumerate(headers):
        stdscr.addstr(start_y, start_x + sum(col_widths[:i]), header, curses.A_BOLD)

    # رسم کادر برای جدول
    draw_box(stdscr, start_y - 1, start_x - 1, sum(col_widths) + len(headers) - 1, len(ovs_info) + 3)

    # نمایش اطلاعات OVS در جدول
    for i, (bridge, port, vlan, vlan_mode, port_status, ip_address) in enumerate(ovs_info):
        stdscr.addstr(start_y + i + 1, start_x, bridge)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0], port)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1], vlan)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2], vlan_mode["Trunk"])
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3], vlan_mode["Access"])
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4], port_status)
        stdscr.addstr(start_y + i + 1, start_x + col_widths[0] + col_widths[1] + col_widths[2] + col_widths[3] + col_widths[4] + col_widths[5], ip_address)

    # نمایش پیام خروج
    message = "Press any key to return to the menu..."
    stdscr.addstr(height - 2, width // 2 - len(message) // 2, message, curses.A_DIM)

    stdscr.refresh()
    stdscr.getch()
