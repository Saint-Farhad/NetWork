import curses
from network_modules.system_info import system_info
from network_modules.dns_config import change_dns
from network_modules.hostname_config import change_hostname
from network_modules.ip_config import change_static_ip
from network_modules.dhcp_config import configure_dhcp
from network_modules.route_config import manage_routes

def network_config_menu(stdscr):
    """
    نمایش منوی تنظیمات شبکه لینوکس برای کاربر.
    کاربر می‌تواند با استفاده از کلیدهای بالا و پایین یا موس گزینه‌ها را انتخاب کند.
    """
    
    # آیتم‌های منو با توضیح کوتاه در مورد هر کدام
    menu_items = [
        "1- Network Interface Information",  # نمایش اطلاعات شبکه
        "2- Change DNS",                     # تغییر تنظیمات DNS
        "3- Change Hostname",                # تغییر نام میزبان
        "4- Change Static IP for Interface", # تنظیم IP استاتیک برای رابط
        "5- Using DHCP to obtain IP",        # تنظیم IP با استفاده از DHCP
        "6- Adding or Removing a Route",     # مدیریت مسیرهای شبکه
        "7- Return to main menu"             # بازگشت به منوی اصلی
    ]

    current_idx = 0  # اندیس فعلی برای آیتم انتخاب‌شده در منو
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن رویدادهای موس

    while True:
        stdscr.clear()  # پاک‌کردن صفحه برای رندر جدید
        height, width = stdscr.getmaxyx()  # دریافت ابعاد صفحه

        # نمایش عنوان در بالای صفحه با استایل بولد و زیرخط‌دار
        title = "Linux Network Configuration"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو و برجسته‌سازی آیتم انتخاب‌شده
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2  # موقعیت افقی آیتم
            y = height // 2 - len(menu_items) // 2 + idx  # موقعیت عمودی آیتم
            if idx == current_idx:  # آیتم انتخاب‌شده را با استایل متفاوت نمایش می‌دهد
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()  # بروزرسانی صفحه

        key = stdscr.getch()  # دریافت ورودی کاربر

        # مدیریت ورودی‌های صفحه‌کلید
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)  # حرکت به سمت بالا در منو
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)  # حرکت به سمت پایین در منو
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب گزینه
            try:
                if current_idx == 0:
                    system_info(stdscr)  # نمایش اطلاعات شبکه
                elif current_idx == 1:
                    change_dns(stdscr)  # تغییر DNS
                elif current_idx == 2:
                    change_hostname(stdscr)  # تغییر نام میزبان
                elif current_idx == 3:
                    change_static_ip(stdscr)  # تنظیم IP استاتیک
                elif current_idx == 4:
                    configure_dhcp(stdscr)  # پیکربندی DHCP
                elif current_idx == 5:
                    manage_routes(stdscr)  # مدیریت مسیرهای شبکه
                elif current_idx == 6:
                    return  # بازگشت به منوی اصلی
            except Exception as e:  # مدیریت خطاها در عملیات شبکه
                stdscr.addstr(height - 2, 0, f"Error: {str(e)}", curses.A_BOLD)
                stdscr.refresh()
                stdscr.getch()  # انتظار برای فشردن کلید جهت ادامه
        elif key == curses.KEY_MOUSE:  # مدیریت رویدادهای موس
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):  # چک کردن کلیک موس روی آیتم‌ها
                    current_idx = idx
                    try:
                        if current_idx == 0:
                            system_info(stdscr)
                        elif current_idx == 1:
                            change_dns(stdscr)
                        elif current_idx == 2:
                            change_hostname(stdscr)
                        elif current_idx == 3:
                            change_static_ip(stdscr)
                        elif current_idx == 4:
                            configure_dhcp(stdscr)
                        elif current_idx == 5:
                            manage_routes(stdscr)
                        elif current_idx == 6:
                            return
                    except Exception as e:  # مدیریت خطاها در صورت کلیک موس
                        stdscr.addstr(height - 2, 0, f"Error: {str(e)}", curses.A_BOLD)
                        stdscr.refresh()
                        stdscr.getch()  # انتظار برای فشردن کلید جهت ادامه
