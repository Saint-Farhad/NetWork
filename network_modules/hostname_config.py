import curses
import subprocess

def get_current_hostname():
    """
    دریافت و بازگرداندن hostname فعلی سیستم.
    از دستور 'hostname' برای این کار استفاده می‌شود.
    """
    try:
        result = subprocess.run("hostname", shell=True, capture_output=True, text=True)
        return result.stdout.strip()  # برگرداندن hostname به صورت رشته تمیز
    except Exception as e:
        return f"Error retrieving hostname: {str(e)}"

def change_hostname(stdscr):
    """
    نمایش منوی تغییر hostname.
    امکان مشاهده و تغییر hostname از طریق این منو وجود دارد.
    """
    menu_items = [
        "1- Show Current Hostname",
        "2- Change Hostname",
        "3- Return to previous menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Hostname Configuration"
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

        key = stdscr.getch()  # دریافت ورودی از صفحه‌کلید

        # مدیریت کلیدها برای حرکت در منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب گزینه
            if current_idx == 0:
                show_current_hostname(stdscr)
            elif current_idx == 1:
                set_new_hostname(stdscr)
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
                        show_current_hostname(stdscr)
                    elif current_idx == 1:
                        set_new_hostname(stdscr)
                    elif current_idx == 2:
                        return
                    break

def show_current_hostname(stdscr):
    """
    نمایش hostname فعلی سیستم.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت hostname فعلی
    current_hostname = get_current_hostname()

    # نمایش hostname فعلی به کاربر
    stdscr.addstr(height // 2 - 2, width // 2 - len("Current Hostname:") // 2, "Current Hostname:", curses.A_BOLD)
    stdscr.addstr(height // 2, width // 2 - len(current_hostname) // 2, current_hostname, curses.A_BOLD)

    # پیغام بازگشت به منو
    stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.refresh()
    stdscr.getch()  # انتظار برای فشردن کلید توسط کاربر

def set_new_hostname(stdscr):
    """
    تغییر hostname سیستم به یک hostname جدید که توسط کاربر وارد شده است.
    """
    curses.echo()  # فعال کردن echo برای نمایش ورودی کاربر
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # نمایش پیغام برای وارد کردن hostname جدید
    stdscr.addstr(height // 2 - 1, width // 2 - len("Enter new hostname: ") // 2, "Enter new hostname: ")
    stdscr.refresh()

    # دریافت hostname جدید از کاربر
    try:
        new_hostname = stdscr.getstr(height // 2, width // 2 - 10, 20).decode('utf-8', errors='ignore').strip()
    except UnicodeDecodeError:
        new_hostname = None  # در صورت بروز خطا در تبدیل، مقدار None قرار می‌گیرد

    curses.noecho()  # غیرفعال کردن echo پس از دریافت ورودی

    # تغییر hostname
    if new_hostname:
        try:
            # اجرای دستور برای تغییر hostname
            subprocess.run(f"sudo hostnamectl set-hostname {new_hostname}", shell=True)

            # نمایش پیغام موفقیت
            success_message = f"Hostname changed to {new_hostname}"
            stdscr.addstr(height // 2 + 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        except Exception as e:
            # نمایش پیغام خطا در صورت بروز مشکل
            error_message = f"Failed to change hostname: {str(e)}"
            stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    else:
        # نمایش پیغام خطا در صورت ورود نام نامعتبر
        error_message = "Invalid hostname. Returning to menu."
        stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD)

    # پیغام بازگشت به منو
    stdscr.addstr(height // 2 + 4, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()  # انتظار برای فشردن کلید توسط کاربر
