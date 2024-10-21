import subprocess
import curses
import logging

# تنظیمات لاگ‌گذاری برای ذخیره عملیات‌ها و خطاها
logging.basicConfig(filename='ovs_bridge_management.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def add_bridge(stdscr):
    """
    تابعی برای اضافه کردن بریج جدید به Open vSwitch.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت نام بریج از کاربر
    stdscr.addstr(height // 2 - 2, width // 2 - 10, "Enter Bridge Name: ")
    curses.echo()
    bridge_name = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        # اجرای دستور برای اضافه کردن بریج به OVS
        subprocess.run(['sudo', 'ovs-vsctl', 'add-br', bridge_name], check=True)
        stdscr.addstr(height // 2, width // 2 - 10, f"Bridge '{bridge_name}' added successfully.")
        logging.info(f"Bridge '{bridge_name}' added successfully.")
    except subprocess.CalledProcessError:
        stdscr.addstr(height // 2, width // 2 - 10, f"Failed to add bridge '{bridge_name}'.")
        logging.error(f"Failed to add bridge '{bridge_name}'.")

    stdscr.addstr(height - 2, width // 2 - 15, "Press any key to return...")
    stdscr.getch()

def view_or_delete_bridges(stdscr):
    """
    تابعی برای مشاهده لیست بریج‌های موجود و امکان حذف آن‌ها.
    """
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        try:
            # اجرای دستور برای دریافت لیست بریج‌های موجود
            result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
            bridges = result.stdout.decode('utf-8').splitlines()
            logging.info("Successfully retrieved bridge list.")
        except subprocess.CalledProcessError:
            bridges = []
            logging.error("Failed to retrieve bridge list.")

        # بررسی اینکه آیا بریجی وجود دارد یا خیر
        if not bridges:
            stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
            stdscr.addstr(height // 2 + 2, width // 2 - len("Press 'q' to return.") // 2, "Press 'q' to return.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('q'):
                return
            continue

        # نمایش لیست بریج‌ها
        stdscr.addstr(1, width // 2 - len("Existing Bridges:") // 2, "Existing Bridges:")
        for idx, bridge in enumerate(bridges):
            stdscr.addstr(3 + idx, width // 2 - len(f"{idx + 1}- {bridge}") // 2, f"{idx + 1}- {bridge}")
        
        stdscr.addstr(len(bridges) + 4, width // 2 - len("Press 'd' to delete a bridge, or 'q' to return.") // 2, "Press 'd' to delete a bridge, or 'q' to return.")
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('q'):
            return
        elif key == ord('d'):
            # دریافت شماره بریج برای حذف
            stdscr.addstr(len(bridges) + 6, width // 2 - len("Enter the bridge number to delete: ") // 2, "Enter the bridge number to delete: ")
            curses.echo()
            choice = stdscr.getstr().decode('utf-8')
            curses.noecho()

            try:
                choice = int(choice) - 1  # تنظیم انتخاب کاربر
                if 0 <= choice < len(bridges):
                    bridge_to_delete = bridges[choice]
                    confirm_msg = f"Are you sure you want to delete bridge '{bridge_to_delete}'? (y/n): "
                    stdscr.addstr(len(bridges) + 7, width // 2 - len(confirm_msg) // 2, confirm_msg)
                    key_confirm = stdscr.getch()

                    if key_confirm == ord('y'):
                        # حذف بریج
                        try:
                            subprocess.run(['sudo', 'ovs-vsctl', 'del-br', bridge_to_delete], check=True)
                            stdscr.addstr(len(bridges) + 8, width // 2 - len(f"Bridge '{bridge_to_delete}' deleted successfully.") // 2, f"Bridge '{bridge_to_delete}' deleted successfully.")
                            logging.info(f"Bridge '{bridge_to_delete}' deleted successfully.")
                        except subprocess.CalledProcessError:
                            stdscr.addstr(len(bridges) + 8, width // 2 - len(f"Failed to delete bridge '{bridge_to_delete}'.") // 2, f"Failed to delete bridge '{bridge_to_delete}'.")
                            logging.error(f"Failed to delete bridge '{bridge_to_delete}'.")
                        stdscr.addstr(len(bridges) + 9, width // 2 - len("Press any key to continue...") // 2, "Press any key to continue...")
                        stdscr.getch()
                    else:
                        logging.info(f"Bridge deletion canceled for '{bridge_to_delete}'.")
                        continue
                else:
                    stdscr.addstr(len(bridges) + 7, width // 2 - len("Invalid choice. Press any key to continue...") // 2, "Invalid choice. Press any key to continue...")
                    logging.warning("Invalid bridge selection.")
                    stdscr.getch()
            except ValueError:
                stdscr.addstr(len(bridges) + 7, width // 2 - len("Invalid input. Press any key to continue...") // 2, "Invalid input. Press any key to continue...")
                logging.warning("Non-numeric input provided.")
                stdscr.getch()
