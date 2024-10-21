import curses
from firewall_modules.firewall_rules import manage_firewall_rules
from firewall_modules.nat_rules import manage_nat_rules  # اضافه کردن واردات nat_rules

def center_text(stdscr, text, row_offset=0):
    """
    نمایش متن در مرکز صفحه با امکان تنظیم فاصله از مرکز.
    
    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    text -- متنی که باید نمایش داده شود
    row_offset -- فاصله‌ای که متن از مرکز به بالا یا پایین منتقل می‌شود
    """
    height, width = stdscr.getmaxyx()  # دریافت ابعاد ترمینال
    x = width // 2 - len(text) // 2  # محاسبه موقعیت افقی برای قرارگیری متن در مرکز
    y = height // 2 + row_offset  # محاسبه موقعیت عمودی با توجه به row_offset
    stdscr.addstr(y, x, text)  # نمایش متن در موقعیت محاسبه‌شده

def firewall_config_menu(stdscr):
    """
    منوی مدیریت فایروال شامل دسترسی به قوانین فایروال و NAT.
    
    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    """
    # آیتم‌های منو برای انتخاب‌های کاربر
    menu_items = [
        "1- Manage Firewall Access Rules",
        "2- Manage NAT Rules",
        "3- Return to main menu"
    ]
    current_idx = 0  # اندیس فعلی برای نشان دادن انتخاب کاربر
    curses.mousemask(curses.ALL_MOUSE_EVENTS)  # فعال کردن پشتیبانی از رویدادهای ماوس

    while True:
        stdscr.clear()  # پاک کردن صفحه قبل از هر بار نمایش منو
        height, width = stdscr.getmaxyx()  # دریافت ابعاد ترمینال

        # نمایش عنوان با استایل بولد و زیرخط‌دار در مرکز صفحه
        title = "Firewall Management"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو به همراه اعداد
        for idx, item in enumerate(menu_items):
            row_offset = idx  # هر آیتم با یک خط فاصله نسبت به قبلی نمایش داده می‌شود
            if idx == current_idx:  # آیتم انتخاب‌شده توسط کاربر
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item, curses.A_REVERSE | curses.A_BOLD)
            else:  # آیتم‌های دیگر
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item)

        stdscr.refresh()  # به‌روزرسانی صفحه

        key = stdscr.getch()  # دریافت ورودی از کاربر

        # مدیریت ورودی‌های صفحه‌کلید
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)  # حرکت به بالا در منو
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)  # حرکت به پایین در منو
        elif key == curses.KEY_ENTER or key in [10, 13]:  # انتخاب آیتم با Enter
            if current_idx == 0:
                manage_firewall_rules(stdscr)  # مدیریت قوانین فایروال
            elif current_idx == 1:
                manage_nat_rules(stdscr)  # مدیریت قوانین NAT
            elif current_idx == 2:
                return  # بازگشت به منوی اصلی
        elif key == curses.KEY_MOUSE:  # مدیریت کلیک‌های ماوس
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                row_offset = idx
                item_y = height // 2 + row_offset
                item_x_start = width // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)
                
                # بررسی موقعیت کلیک ماوس نسبت به آیتم‌های منو
                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        manage_firewall_rules(stdscr)
                    elif current_idx == 1:
                        manage_nat_rules(stdscr)
                    elif current_idx == 2:
                        return
                    break
