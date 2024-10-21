import curses
from welcome import draw_welcome_screen  # نمایش صفحه خوش‌آمدگویی
from menu import draw_menu  # نمایش منوی اصلی
from network_config import network_config_menu  # منوی پیکربندی شبکه
from firewall_config import firewall_config_menu  # منوی فایروال

def main(stdscr):
    """
    تابع اصلی برنامه برای اجرای صفحه خوش‌آمدگویی و منوی اصلی.

    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    curses.curs_set(0)  # غیرفعال کردن مکان‌نما برای بهبود تجربه کاربری

    # نمایش صفحه خوش‌آمدگویی
    draw_welcome_screen(stdscr)

    # حلقه اصلی برنامه برای نمایش منو و مدیریت انتخاب‌ها
    while True:
        choice = draw_menu(stdscr)  # فراخوانی منوی اصلی و دریافت انتخاب کاربر
        
        # مدیریت انتخاب کاربر و فراخوانی منوهای مربوطه
        if choice == 0:
            network_config_menu(stdscr)  # فراخوانی منوی پیکربندی شبکه
        elif choice == 1:
            firewall_config_menu(stdscr)  # فراخوانی منوی مدیریت فایروال
        elif choice == 5:
            break  # خروج از برنامه

if __name__ == "__main__":
    curses.wrapper(main)
