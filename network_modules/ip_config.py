import curses
import subprocess
import os

def change_static_ip(stdscr):
    """
    نمایش منوی اصلی برای تغییر IP استاتیک. کاربر می‌تواند بین تنظیم موقت و دائمی IP استاتیک یکی را انتخاب کند.
    """
    menu_items = [
        "1- Temporary IP Static Change",
        "2- Permanent IP Static Change",
        "3- Return to previous menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Change Static IP for Interface"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب شده
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()  # دریافت ورودی از صفحه‌کلید

        # مدیریت کلیدها برای حرکت در منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب آیتم
            if current_idx == 0:
                temp_ip_menu(stdscr)  # فراخوانی منوی IP موقت
            elif current_idx == 1:
                perm_ip_menu(stdscr)  # فراخوانی منوی IP دائمی
            elif current_idx == 2:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:  # مدیریت کلیک ماوس
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        temp_ip_menu(stdscr)
                    elif current_idx == 1:
                        perm_ip_menu(stdscr)
                    elif current_idx == 2:
                        return
                    break

def temp_ip_menu(stdscr):
    """
    نمایش منوی تنظیم IP موقت. کاربر می‌تواند IP استاتیک موقت اضافه کند یا آن را حذف کند.
    """
    menu_items = [
        "1- Add Temporary Static IP",
        "2- Remove Temporary Static IP",
        "3- Return to previous menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Temporary Static IP Management"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب شده
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()

        # مدیریت کلیدها برای حرکت در منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب آیتم
            if current_idx == 0:
                set_temp_static_ip(stdscr)  # اضافه کردن IP موقت
            elif current_idx == 1:
                remove_temp_static_ip(stdscr)  # حذف IP موقت
            elif current_idx == 2:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        set_temp_static_ip(stdscr)
                    elif current_idx == 1:
                        remove_temp_static_ip(stdscr)
                    elif current_idx == 2:
                        return
                    break

def perm_ip_menu(stdscr):
    """
    نمایش منوی تنظیم IP دائمی. کاربر می‌تواند IP استاتیک دائمی اضافه کند یا آن را حذف کند.
    """
    menu_items = [
        "1- Add Permanent Static IP",
        "2- Remove Permanent Static IP",
        "3- Return to previous menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Permanent Static IP Management"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()

        # مدیریت انتخاب آیتم‌های منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                set_perm_static_ip(stdscr)  # اضافه کردن IP دائمی
            elif current_idx == 1:
                remove_perm_static_ip(stdscr)  # حذف IP دائمی
            elif current_idx == 2:
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        set_perm_static_ip(stdscr)
                    elif current_idx == 1:
                        remove_perm_static_ip(stdscr)
                    elif current_idx == 2:
                        return
                    break

def set_temp_static_ip(stdscr):
    """
    اضافه کردن IP استاتیک موقت به یک اینترفیس مشخص.
    """
    curses.echo()  # فعال کردن echo برای نمایش ورودی کاربر
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت نام اینترفیس
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter interface (e.g., eth0): ") // 2, "Enter interface (e.g., eth0): ")
    stdscr.refresh()
    interface = stdscr.getstr(height // 2 - 1, width // 2 - 10, 20).decode().strip()

    # دریافت IP استاتیک جدید
    stdscr.addstr(height // 2, width // 2 - len("Enter new static IP (e.g., 192.168.1.100): ") // 2, "Enter new static IP (e.g., 192.168.1.100): ")
    stdscr.refresh()
    static_ip = stdscr.getstr(height // 2 + 1, width // 2 - 10, 20).decode().strip()
    curses.noecho()

    # اعتبارسنجی ورودی‌ها
    if interface and static_ip:
        # اجرای دستور برای اضافه کردن IP استاتیک موقت
        result = subprocess.run(f"sudo ip addr add {static_ip}/24 dev {interface}", shell=True, capture_output=True, text=True)

        # بررسی موفقیت یا عدم موفقیت عملیات
        if result.returncode == 0:
            success_message = f"Temporary IP {static_ip} set successfully on {interface}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        else:
            error_message = f"Failed to set IP: {result.stderr.strip()}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Returning to menu."
        stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    # نمایش پیغام برای بازگشت به منو
    stdscr.addstr(height // 2 + 5, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def remove_temp_static_ip(stdscr):
    """
    حذف IP استاتیک موقت از یک اینترفیس.
    """
    curses.echo()
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت نام اینترفیس
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter interface (e.g., eth0): ") // 2, "Enter interface (e.g., eth0): ")
    stdscr.refresh()
    interface = stdscr.getstr(height // 2 - 1, width // 2 - 10, 20).decode().strip()

    # دریافت IP برای حذف
    stdscr.addstr(height // 2, width // 2 - len("Enter IP to remove (e.g., 192.168.1.100): ") // 2, "Enter IP to remove (e.g., 192.168.1.100): ")
    stdscr.refresh()
    static_ip = stdscr.getstr(height // 2 + 1, width // 2 - 10, 20).decode().strip()
    curses.noecho()

    # اعتبارسنجی ورودی‌ها
    if interface and static_ip:
        # اجرای دستور برای حذف IP استاتیک موقت
        result = subprocess.run(f"sudo ip addr del {static_ip}/24 dev {interface}", shell=True, capture_output=True, text=True)

        # بررسی موفقیت یا عدم موفقیت عملیات
        if result.returncode == 0:
            success_message = f"Temporary IP {static_ip} removed successfully from {interface}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        else:
            error_message = f"Failed to remove IP: {result.stderr.strip()}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Returning to menu."
        stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    # نمایش پیغام برای بازگشت به منو
    stdscr.addstr(height // 2 + 5, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def set_perm_static_ip(stdscr):
    """
    اضافه کردن IP استاتیک دائمی به یک اینترفیس. فایل /etc/network/interfaces ویرایش می‌شود.
    """
    curses.echo()
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت نام اینترفیس
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter interface (e.g., eth0): ") // 2, "Enter interface (e.g., eth0): ")
    stdscr.refresh()
    interface = stdscr.getstr(height // 2 - 1, width // 2 - 10, 20).decode().strip()

    # دریافت IP جدید
    stdscr.addstr(height // 2, width // 2 - len("Enter new static IP (e.g., 192.168.1.100): ") // 2, "Enter new static IP (e.g., 192.168.1.100): ")
    stdscr.refresh()
    static_ip = stdscr.getstr(height // 2 + 1, width // 2 - 10, 20).decode().strip()
    curses.noecho()

    # اعتبارسنجی ورودی‌ها
    if interface and static_ip:
        try:
            # نوشتن IP استاتیک در فایل /etc/network/interfaces (مخصوص توزیع‌های مبتنی بر Debian)
            config_line = f"iface {interface} inet static\n    address {static_ip}\n    netmask 255.255.255.0\n"
            with open("/etc/network/interfaces", "a") as f:
                f.write(f"\n{config_line}")

            success_message = f"Permanent IP {static_ip} set successfully on {interface}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        except Exception as e:
            error_message = f"Failed to set IP: {str(e)}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Returning to menu."
        stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    # نمایش پیغام برای بازگشت به منو
    stdscr.addstr(height // 2 + 5, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def remove_perm_static_ip(stdscr):
    """
    حذف IP استاتیک دائمی از فایل /etc/network/interfaces برای یک اینترفیس مشخص.
    """
    curses.echo()
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت نام اینترفیس
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter interface (e.g., eth0): ") // 2, "Enter interface (e.g., eth0): ")
    stdscr.refresh()
    interface = stdscr.getstr(height // 2 - 1, width // 2 - 10, 20).decode().strip()

    # دریافت IP برای حذف
    stdscr.addstr(height // 2, width // 2 - len("Enter IP to remove (e.g., 192.168.1.100): ") // 2, "Enter IP to remove (e.g., 192.168.1.100): ")
    stdscr.refresh()
    static_ip = stdscr.getstr(height // 2 + 1, width // 2 - 10, 20).decode().strip()
    curses.noecho()

    # اعتبارسنجی ورودی‌ها
    if interface and static_ip:
        try:
            # خواندن فایل /etc/network/interfaces و حذف خطوط مرتبط با IP و اینترفیس
            with open("/etc/network/interfaces", "r") as f:
                lines = f.readlines()

            with open("/etc/network/interfaces", "w") as f:
                skip = False
                for line in lines:
                    if line.strip() == f"iface {interface} inet static":
                        skip = True
                    elif skip and "address" in line and static_ip in line:
                        skip = False  # خطوط مرتبط با IP و netmask حذف می‌شوند
                        continue
                    elif skip and "netmask" in line:
                        continue
                    else:
                        f.write(line)

            success_message = f"Permanent IP {static_ip} removed successfully from {interface}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        except Exception as e:
            error_message = f"Failed to remove IP: {str(e)}"
            stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Returning to menu."
        stdscr.addstr(height // 2 + 3, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    # نمایش پیغام برای بازگشت به منو
    stdscr.addstr(height // 2 + 5, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()
