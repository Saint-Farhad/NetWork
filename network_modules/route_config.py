import curses
import subprocess

def manage_routes(stdscr):
    """
    نمایش منوی مدیریت روت‌ها. کاربر می‌تواند روت‌های موقت و دائمی را اضافه یا حذف کند.
    """
    route_menu = [
        "1- Add Temporary Route",
        "2- Add Permanent Route",
        "3- Remove Temporary Route",
        "4- Remove Permanent Route",
        "5- Return to previous menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # عنوان در وسط صفحه
        title = "Manage Routes"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(route_menu):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(route_menu) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب‌شده
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()

        # مدیریت انتخاب آیتم‌ها
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(route_menu)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(route_menu)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب آیتم
            if current_idx == 0:
                add_temp_route(stdscr)  # اضافه کردن روت موقت
            elif current_idx == 1:
                add_perm_route(stdscr)  # اضافه کردن روت دائمی
            elif current_idx == 2:
                remove_temp_route(stdscr)  # حذف روت موقت
            elif current_idx == 3:
                remove_perm_route(stdscr)  # حذف روت دائمی
            elif current_idx == 4:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(route_menu):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(route_menu) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        add_temp_route(stdscr)
                    elif current_idx == 1:
                        add_perm_route(stdscr)
                    elif current_idx == 2:
                        remove_temp_route(stdscr)
                    elif current_idx == 3:
                        remove_perm_route(stdscr)
                    elif current_idx == 4:
                        return
                    break

def add_temp_route(stdscr):
    """
    اضافه کردن یک روت موقت به شبکه.
    """
    stdscr.clear()
    curses.echo()
    height, width = stdscr.getmaxyx()

    # دریافت مقصد
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter destination (e.g., 192.168.1.0/24): ") // 2, "Enter destination (e.g., 192.168.1.0/24): ")
    stdscr.refresh()
    destination = stdscr.getstr(height // 2 - 1, width // 2 - 10, 40).decode().strip()

    # دریافت گیت‌وی
    stdscr.addstr(height // 2, width // 2 - len("Enter gateway (e.g., 192.168.1.1): ") // 2, "Enter gateway (e.g., 192.168.1.1): ")
    stdscr.refresh()
    gateway = stdscr.getstr(height // 2 + 1, width // 2 - 10, 40).decode().strip()
    curses.noecho()

    stdscr.clear()

    if destination and gateway:
        # افزودن روت موقت
        result = subprocess.run(f"sudo ip route add {destination} via {gateway}", shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            success_message = f"Temporary route to {destination} via {gateway} added."
            stdscr.addstr(height // 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        else:
            error_message = f"Failed to add route: {result.stderr.strip()[:width - 2]}"  # محدود کردن طول پیام خطا
            stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Please provide both destination and gateway."
        stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()

def remove_temp_route(stdscr):
    """
    حذف یک روت موقت از شبکه.
    """
    stdscr.clear()
    curses.echo()
    height, width = stdscr.getmaxyx()

    # دریافت مقصد برای حذف
    prompt = "Enter destination to remove (e.g., 192.168.1.0/24): "
    stdscr.addstr(height // 2 - 2, width // 2 - len(prompt) // 2, prompt)
    stdscr.refresh()
    destination = stdscr.getstr(height // 2 - 1, width // 2 - 15, 30).decode().strip()
    curses.noecho()

    stdscr.clear()

    if destination:
        # حذف روت موقت
        result = subprocess.run(f"sudo ip route del {destination}", shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            success_message = f"Temporary route to {destination} removed."
            stdscr.addstr(height // 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        else:
            error_message = f"Failed to remove route: {result.stderr.strip()[:width - 2]}"  # محدود کردن طول پیام خطا
            stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "No destination provided. Returning to menu."
        stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()

def add_perm_route(stdscr):
    """
    اضافه کردن یک روت دائمی به شبکه با ویرایش فایل /etc/network/interfaces.
    """
    stdscr.clear()
    curses.echo()
    height, width = stdscr.getmaxyx()

    # دریافت مقصد
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter destination (e.g., 192.168.1.0/24): ") // 2, "Enter destination (e.g., 192.168.1.0/24): ")
    stdscr.refresh()
    destination = stdscr.getstr(height // 2 - 1, width // 2 - 10, 40).decode().strip()

    # دریافت گیت‌وی
    stdscr.addstr(height // 2, width // 2 - len("Enter gateway (e.g., 192.168.1.1): ") // 2, "Enter gateway (e.g., 192.168.1.1): ")
    stdscr.refresh()
    gateway = stdscr.getstr(height // 2 + 1, width // 2 - 10, 40).decode().strip()
    curses.noecho()

    stdscr.clear()

    if destination and gateway:
        # افزودن روت دائمی به فایل /etc/network/interfaces
        try:
            with open("/etc/network/interfaces", "a") as f:
                f.write(f"\nup route add -net {destination} gw {gateway}\n")

            success_message = f"Permanent route to {destination} via {gateway} added."
            stdscr.addstr(height // 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        except Exception as e:
            error_message = f"Failed to add permanent route: {str(e)[:width - 2]}"  # محدود کردن طول پیام
            stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "Invalid input. Please provide both destination and gateway."
        stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()

def remove_perm_route(stdscr):
    """
    حذف یک روت دائمی از فایل /etc/network/interfaces.
    """
    stdscr.clear()
    curses.echo()
    height, width = stdscr.getmaxyx()

    # دریافت مقصد برای حذف
    stdscr.addstr(height // 2 - 2, width // 2 - len("Enter destination to remove (e.g., 192.168.1.0/24): ") // 2, "Enter destination to remove (e.g., 192.168.1.0/24): ")
    stdscr.refresh()
    destination = stdscr.getstr(height // 2 - 1, width // 2 - 10, 40).decode().strip()
    curses.noecho()

    stdscr.clear()

    if destination:
        # حذف روت دائمی از فایل /etc/network/interfaces
        try:
            with open("/etc/network/interfaces", "r") as f:
                lines = f.readlines()

            # نوشتن مجدد فایل بدون روت مورد نظر
            with open("/etc/network/interfaces", "w") as f:
                for line in lines:
                    if f"up route add -net {destination}" not in line:
                        f.write(line)

            success_message = f"Permanent route to {destination} removed."
            stdscr.addstr(height // 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        except Exception as e:
            error_message = f"Failed to remove permanent route: {str(e)[:width - 2]}"  # محدود کردن طول پیام
            stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        error_message = "No destination provided. Returning to menu."
        stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()
