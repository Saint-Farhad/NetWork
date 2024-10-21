import curses
import subprocess

def change_dns(stdscr):
    """
    نمایش منوی تغییر DNS. کاربر می‌تواند بین تنظیم موقت یا دائمی DNS انتخاب کند.
    """
    dns_menu = [
        "1- Temporary DNS Change",
        "2- Permanent DNS Change",
        "3- Return to previous menu"
    ]
    current_idx = 0

    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = "Change DNS"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو و برجسته‌سازی آیتم انتخاب‌شده
        for idx, item in enumerate(dns_menu):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(dns_menu) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()  # دریافت ورودی از کاربر

        # مدیریت ورودی صفحه کلید برای حرکت بین آیتم‌ها
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(dns_menu)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(dns_menu)
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب آیتم منو
            if current_idx == 0:
                temp_dns_menu(stdscr)  # تغییر موقت DNS
            elif current_idx == 1:
                perm_dns_menu(stdscr)  # تغییر دائمی DNS
            elif current_idx == 2:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:  # مدیریت کلیک ماوس
            _, mx, my, _, _ = curses.getmouse()

            # بررسی کلیک ماوس روی آیتم‌ها
            for idx, item in enumerate(dns_menu):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(dns_menu) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        temp_dns_menu(stdscr)
                    elif current_idx == 1:
                        perm_dns_menu(stdscr)
                    elif current_idx == 2:
                        return
                    break

def temp_dns_menu(stdscr):
    """
    نمایش منوی تغییر موقت DNS و ارائه گزینه‌هایی برای انتخاب DNS سرورهای استاندارد یا سفارشی.
    """
    dns_options = [
        "1- Google Public DNS (8.8.8.8, 8.8.4.4)",
        "2- Cloudflare DNS (1.1.1.1, 1.0.0.1)",
        "3- Open DNS (208.67.222.222, 208.67.220.220)",
        "4- Quad9 DNS (9.9.9.9, 149.112.112.112)",
        "5- Shecan DNS (178.22.122.100, 185.51.200.2)",
        "6- Custom DNS",
        "7- Return to previous menu"
    ]
    current_idx = 0

    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = "Temporary DNS Change"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو و برجسته‌سازی آیتم انتخاب‌شده
        for idx, item in enumerate(dns_options):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(dns_options) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()

        # مدیریت انتخاب DNS سرور یا سفارشی
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(dns_options)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(dns_options)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx in range(0, 5):  # تنظیم DNS سرورهای استاندارد
                dns_servers = {
                    0: "8.8.8.8 8.8.4.4",
                    1: "1.1.1.1 1.0.0.1",
                    2: "208.67.222.222 208.67.220.220",
                    3: "9.9.9.9 149.112.112.112",
                    4: "178.22.122.100 185.51.200.2"
                }
                set_temp_dns(stdscr, dns_servers[current_idx])
            elif current_idx == 5:
                custom_dns(stdscr)  # تنظیم DNS سفارشی
            elif current_idx == 6:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:  # مدیریت کلیک ماوس روی آیتم‌های منو
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(dns_options):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(dns_options) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx in range(0, 5):
                        dns_servers = {
                            0: "8.8.8.8 8.8.4.4",
                            1: "1.1.1.1 1.0.0.1",
                            2: "208.67.222.222 208.67.220.220",
                            3: "9.9.9.9 149.112.112.112",
                            4: "178.22.122.100 185.51.200.2"
                        }
                        set_temp_dns(stdscr, dns_servers[current_idx])
                    elif current_idx == 5:
                        custom_dns(stdscr)
                    elif current_idx == 6:
                        return
                    break

def set_temp_dns(stdscr, dns):
    """
    تابعی برای تنظیم موقت DNS بر روی اینترفیس مشخص شده. از دستور resolvectl استفاده می‌شود.
    """
    stdscr.clear()
    message = f"Setting temporary DNS to {dns}..."
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height // 2, width // 2 - len(message) // 2, message)
    stdscr.refresh()

    interface = "eth0"  # تغییر نام اینترفیس در صورت نیاز
    try:
        result = subprocess.run(
            f"sudo resolvectl dns {interface} {dns}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10  # اضافه کردن تایم‌اوت برای جلوگیری از فریز شدن
        )
        if result.returncode == 0:
            success_message = "Temporary DNS set successfully."
            stdscr.addstr(height // 2 + 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
        else:
            error_message = f"Failed to set DNS: {result.stderr.strip()}"
            stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)
    except subprocess.TimeoutExpired:
        error_message = "Failed to set DNS: Connection timed out."
        stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)

    # پیام بازگشت به منو
    stdscr.addstr(height // 2 + 4, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def custom_dns(stdscr):
    """
    دریافت DNS سفارشی از کاربر و اعمال آن به صورت موقت.
    """
    curses.echo()  # فعال کردن echo برای نمایش ورودی کاربر
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    prompt = "Enter custom DNS (separate by space): "
    stdscr.addstr(height // 2 - 1, width // 2 - len(prompt) // 2, prompt)
    stdscr.refresh()
    dns_input = stdscr.getstr(height // 2, width // 2 - 10, 40).decode().strip()
    curses.noecho()  # غیرفعال کردن echo پس از دریافت ورودی

    if dns_input:
        set_temp_dns(stdscr, dns_input)  # تنظیم DNS سفارشی
    else:
        error_message = "No DNS entered. Returning to menu."
        stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BLINK)
        stdscr.addstr(height // 2 + 4, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
        stdscr.refresh()
        stdscr.getch()

def perm_dns_menu(stdscr):
    """
    نمایش منوی تغییر دائمی DNS.
    """
    dns_options = [
        "1- Google Public DNS (8.8.8.8, 8.8.4.4)",
        "2- Cloudflare DNS (1.1.1.1, 1.0.0.1)",
        "3- Open DNS (208.67.222.222, 208.67.220.220)",
        "4- Quad9 DNS (9.9.9.9, 149.112.112.112)",
        "5- Shecan DNS (178.22.122.100, 185.51.200.2)",
        "6- Custom DNS",
        "7- Return to previous menu"
    ]
    current_idx = 0

    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از ماوس

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        title = "Permanent DNS Change"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        for idx, item in enumerate(dns_options):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(dns_options) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(dns_options)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(dns_options)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx in range(0, 5):
                dns_servers = {
                    0: "8.8.8.8 8.8.4.4",
                    1: "1.1.1.1 1.0.0.1",
                    2: "208.67.222.222 208.67.220.220",
                    3: "9.9.9.9 149.112.112.112",
                    4: "178.22.122.100 185.51.200.2"
                }
                set_perm_dns(stdscr, dns_servers[current_idx])  # تنظیم دائمی DNS
            elif current_idx == 5:
                custom_perm_dns(stdscr)  # تنظیم DNS سفارشی
            elif current_idx == 6:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:  # مدیریت کلیک ماوس
            _, mx, my, _, _ = curses.getmouse()

            # بررسی کلیک ماوس روی آیتم‌ها
            for idx, item in enumerate(dns_options):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(dns_options) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx in range(0, 5):
                        dns_servers = {
                            0: "8.8.8.8 8.8.4.4",
                            1: "1.1.1.1 1.0.0.1",
                            2: "208.67.222.222 208.67.220.220",
                            3: "9.9.9.9 149.112.112.112",
                            4: "178.22.122.100 185.51.200.2"
                        }
                        set_perm_dns(stdscr, dns_servers[current_idx])
                    elif current_idx == 5:
                        custom_perm_dns(stdscr)
                    elif current_idx == 6:
                        return
                    break

def set_perm_dns(stdscr, dns):
    """
    تنظیم دائمی DNS با ویرایش فایل /etc/resolv.conf.
    """
    stdscr.clear()
    message = f"Setting permanent DNS to {dns}..."
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height // 2, width // 2 - len(message) // 2, message)
    stdscr.refresh()

    try:
        # بازنویسی فایل resolv.conf برای تنظیم DNS دائمی
        with open("/etc/resolv.conf", "w") as f:
            dns_servers = dns.split()
            for server in dns_servers:
                f.write(f"nameserver {server}\n")
        
        success_message = "Permanent DNS set successfully."
        stdscr.addstr(height // 2 + 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD)
    except Exception as e:
        error_message = f"Failed to set DNS: {str(e)}"
        stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)

    stdscr.addstr(height // 2 + 4, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
    stdscr.refresh()
    stdscr.getch()

def custom_perm_dns(stdscr):
    """
    دریافت DNS سفارشی برای تنظیم دائمی از کاربر.
    """
    curses.echo()
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    prompt = "Enter custom permanent DNS (separate by space): "
    stdscr.addstr(height // 2 - 1, width // 2 - len(prompt) // 2, prompt)
    stdscr.refresh()
    dns_input = stdscr.getstr(height // 2, width // 2 - 10, 40).decode().strip()
    curses.noecho()

    if dns_input:
        set_perm_dns(stdscr, dns_input)  # تنظیم DNS سفارشی
    else:
        error_message = "No DNS entered. Returning to menu."
        stdscr.addstr(height // 2 + 2, width // 2 - len(error_message) // 2, error_message, curses.A_BLINK)
        stdscr.addstr(height // 2 + 4, width // 2 - len("Press any key to return to the menu...") // 2, "Press any key to return to the menu...")
        stdscr.refresh()
        stdscr.getch()
