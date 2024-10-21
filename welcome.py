import curses
import time

def draw_welcome_screen(stdscr):
    # تنظیم رنگ‌ها
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # متن خوش آمد
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # نوار پیشرفت اولیه
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # نوار پیشرفت نهایی
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)  # متن نهایی TakTourAndaz
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)  # رنگ سفید برای متن

    # پاک کردن صفحه
    stdscr.clear()

    # گرفتن اندازه ترمینال
    height, width = stdscr.getmaxyx()

    # تنظیمات متن خوش آمد
    welcome_text = "Welcome to the Network Configuration and Monitoring Tool."
    taktourandaz_text = "TakTourAndaz 6 !"

    # موقعیت یابی متن خوش آمد
    x_welcome = width // 2 - len(welcome_text) // 2
    y_welcome = height // 2 - 4

    # موقعیت یابی متن TakTourAndaz
    x_tak = width // 2 - len(taktourandaz_text) // 2
    y_tak = height // 2 + 4

    # نوار پیشرفت
    progress_bar_length = 60  # طول نوار پیشرفت
    x_progress = width // 2 - (progress_bar_length + 2) // 2
    y_progress = height // 2  # نوار پیشرفت دقیقاً بین دو عبارت

    # نمایش تدریجی متن خوش آمد و TakTourAndaz همزمان با نوار پیشرفت
    for i in range(101):
        # نمایش کاراکترهای متن‌ها همزمان با نوار پیشرفت
        if i * len(welcome_text) // 100 < len(welcome_text):
            stdscr.addstr(y_welcome, x_welcome + i * len(welcome_text) // 100, welcome_text[i * len(welcome_text) // 100], curses.color_pair(1) | curses.A_BOLD)

        if i * len(taktourandaz_text) // 100 < len(taktourandaz_text):
            stdscr.addstr(y_tak, x_tak + i * len(taktourandaz_text) // 100, taktourandaz_text[i * len(taktourandaz_text) // 100], curses.color_pair(4) | curses.A_BOLD)

        # نمایش نوار پیشرفت با تغییر تدریجی رنگ
        if i < 50:
            color_pair = curses.color_pair(2)  # نیمی از پیشرفت به رنگ زرد
        else:
            color_pair = curses.color_pair(3)  # نیمی دیگر به رنگ سبز

        progress_bar = "[" + "#" * (i * progress_bar_length // 100) + " " * (progress_bar_length - (i * progress_bar_length // 100)) + "]"
        stdscr.addstr(y_progress, x_progress, progress_bar, color_pair | curses.A_BOLD)

        stdscr.refresh()
        time.sleep(0.05)  # تنظیم سرعت

    # مکث قبل از پاک کردن صفحه
    time.sleep(2)

    # پاک کردن صفحه پس از نمایش
    stdscr.clear()
    stdscr.refresh()
