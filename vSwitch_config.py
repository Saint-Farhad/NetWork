import curses
from ovs_modules.ovs_bridge import add_bridge, view_or_delete_bridges
from ovs_modules.ovs_port import manage_ovs_ports
from ovs_modules.ovs_vlan import create_vlan_interface, set_ip_for_vlan, set_vlan_for_trunk, delete_vlan_interface
from ovs_modules.ovs_status import show_ovs_status
import logging

# تنظیمات اولیه برای لاگ‌گذاری
logging.basicConfig(filename='ovs_management.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def manage_vs_main_menu(stdscr):
    """
    مدیریت منوی اصلی Open vSwitch، شامل مدیریت بریج‌ها، پورت‌ها، VLAN و وضعیت OVS.
    """
    menu_items = [
        "1- Bridge Management",
        "2- Port Management",
        "3- VLAN Management",
        "4- Show OVS Status",  # اضافه شدن گزینه نمایش وضعیت OVS
        "5- Return to Main Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Open vSwitch Management"
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

        # مدیریت کلیدهای جهت‌دار برای جابه‌جایی بین آیتم‌های منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # انتخاب آیتم منو بر اساس گزینه انتخابی
            if current_idx == 0:
                logging.info("Bridge management selected")
                manage_ovs_bridges(stdscr)
            elif current_idx == 1:
                logging.info("Port management selected")
                manage_ovs_ports(stdscr)
            elif current_idx == 2:
                logging.info("VLAN management selected")
                manage_ovs_vlans(stdscr)
            elif current_idx == 3:
                logging.info("Show OVS status selected")
                show_ovs_status(stdscr)  # نمایش وضعیت OVS
            elif current_idx == 4:
                logging.info("Return to main menu selected")
                return
        elif key == curses.KEY_MOUSE:
            # مدیریت کلیک ماوس
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        logging.info("Bridge management selected via mouse")
                        manage_ovs_bridges(stdscr)
                    elif current_idx == 1:
                        logging.info("Port management selected via mouse")
                        manage_ovs_ports(stdscr)
                    elif current_idx == 2:
                        logging.info("VLAN management selected via mouse")
                        manage_ovs_vlans(stdscr)
                    elif current_idx == 3:
                        logging.info("Show OVS status selected via mouse")
                        show_ovs_status(stdscr)
                    elif current_idx == 4:
                        logging.info("Return to main menu selected via mouse")
                        return
                    break


def manage_ovs_bridges(stdscr):
    """
    مدیریت بریج‌های Open vSwitch: اضافه یا حذف بریج‌ها.
    """
    menu_items = [
        "1- Add Bridge",
        "2- View or Delete Bridges",
        "3- Return to Previous Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Open vSwitch Bridge Management"
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

        # مدیریت جابه‌جایی در منوی بریج‌ها
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                logging.info("Add bridge selected")
                add_bridge(stdscr)
            elif current_idx == 1:
                logging.info("View or delete bridges selected")
                view_or_delete_bridges(stdscr)
            elif current_idx == 2:
                logging.info("Return to previous menu selected")
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        logging.info("Add bridge selected via mouse")
                        add_bridge(stdscr)
                    elif current_idx == 1:
                        logging.info("View or delete bridges selected via mouse")
                        view_or_delete_bridges(stdscr)
                    elif current_idx == 2:
                        logging.info("Return to previous menu selected via mouse")
                        return
                    break


def manage_ovs_vlans(stdscr):
    """
    مدیریت VLAN‌ها در Open vSwitch، شامل ایجاد، حذف و تنظیمات VLAN.
    """
    menu_items = [
        "1- Create VLAN Interface",
        "2- Set IP for VLAN Interface",
        "3- Set VLAN for Trunk Port",
        "4- Delete VLAN Interface",
        "5- Return to Previous Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "VLAN Management"
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

        # مدیریت گزینه‌های VLAN
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                logging.info("Create VLAN interface selected")
                create_vlan_interface(stdscr)
            elif current_idx == 1:
                logging.info("Set IP for VLAN interface selected")
                set_ip_for_vlan(stdscr)
            elif current_idx == 2:
                logging.info("Set VLAN for trunk port selected")
                set_vlan_for_trunk(stdscr)
            elif current_idx == 3:
                logging.info("Delete VLAN interface selected")
                delete_vlan_interface(stdscr)
            elif current_idx == 4:
                logging.info("Return to previous menu selected")
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        logging.info("Create VLAN interface selected via mouse")
                        create_vlan_interface(stdscr)
                    elif current_idx == 1:
                        logging.info("Set IP for VLAN interface selected via mouse")
                        set_ip_for_vlan(stdscr)
                    elif current_idx == 2:
                        logging.info("Set VLAN for trunk port selected via mouse")
                        set_vlan_for_trunk(stdscr)
                    elif current_idx == 3:
                        logging.info("Delete VLAN interface selected via mouse")
                        delete_vlan_interface(stdscr)
                    elif current_idx == 4:
                        logging.info("Return to previous menu selected via mouse")
                        return
                    break
