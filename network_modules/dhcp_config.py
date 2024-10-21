import curses
import subprocess

def configure_dhcp(stdscr):
    """
    تابعی برای پیکربندی DHCP بر روی یک اینترفیس شبکه.
    از کاربر نام اینترفیس گرفته شده و سپس DHCP فعال می‌شود.
    اگر مشکلی در تنظیم DHCP وجود داشته باشد، خطا نمایش داده می‌شود.
    """

    curses.echo()  # فعال کردن حالت echo برای اینکه کاربر بتواند ورودی خود را مشاهده کند
    stdscr.clear()  # پاک کردن صفحه
    height, width = stdscr.getmaxyx()  # دریافت ابعاد ترمینال

    # نمایش عنوان
    title = "Using DHCP to obtain IP"
    stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

    # درخواست نام اینترفیس از کاربر
    prompt = "Enter interface (e.g., eth0): "
    stdscr.addstr(height // 2 - 2, width // 2 - len(prompt) // 2, prompt)
    stdscr.refresh()  # بروزرسانی صفحه
    interface = stdscr.getstr(height // 2 - 1, width // 2 - 10, 20).decode().strip()  # دریافت ورودی کاربر
    curses.noecho()  # غیرفعال کردن echo بعد از دریافت ورودی

    if interface:  # اگر نام اینترفیس وارد شده باشد
        stdscr.clear()

        # نمایش پیغام در حال انجام تنظیمات DHCP
        processing_message = f"Configuring DHCP for {interface}..."
        stdscr.addstr(height // 2, width // 2 - len(processing_message) // 2, processing_message, curses.A_BOLD)
        stdscr.refresh()

        try:
            # اجرای دستور dhclient برای فعال‌سازی DHCP بر روی اینترفیس
            result = subprocess.run(f"sudo dhclient {interface}", shell=True, capture_output=True, text=True)

            # بررسی وضعیت موفقیت آمیز بودن یا نبودن عملیات DHCP
            stdscr.clear()
            if result.returncode == 0:  # اگر DHCP موفقیت‌آمیز باشد
                success_message = f"DHCP configured successfully for {interface}."
                stdscr.addstr(height // 2, width // 2 - len(success_message) // 2, success_message, curses.A_BOLD | curses.A_UNDERLINE)
            else:  # اگر خطایی رخ دهد
                error_message = f"Failed to configure DHCP: {result.stderr.strip()}"
                stdscr.addstr(height // 2, width // 2 - len(error_message) // 2, error_message, curses.A_BOLD | curses.A_BLINK)

        except Exception as e:  # مدیریت خطاهای احتمالی که در هنگام اجرای دستور رخ دهد
            stdscr.clear()
            exception_message = f"An error occurred: {str(e)}"
            stdscr.addstr(height // 2, width // 2 - len(exception_message) // 2, exception_message, curses.A_BOLD | curses.A_BLINK)

    else:  # اگر کاربر نام اینترفیس را وارد نکرده باشد
        stdscr.clear()
        no_interface_message = "No interface provided. Returning to menu..."
        stdscr.addstr(height // 2, width // 2 - len(no_interface_message) // 2, no_interface_message, curses.A_BOLD | curses.A_BLINK)

    # نمایش پیام برای بازگشت به منو
    return_message = "Press any key to return to the menu..."
    stdscr.addstr(height // 2 + 2, width // 2 - len(return_message) // 2, return_message, curses.A_DIM)
    stdscr.refresh()
    stdscr.getch()  # انتظار برای فشردن یک کلید توسط کاربر برای بازگشت به منوی اصلی
