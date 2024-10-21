import curses
import subprocess

def manage_ovs_ports(stdscr):
    """
    مدیریت پورت‌های Open vSwitch (اضافه کردن پورت، تغییر وضعیت پورت، 
    تنظیم حالت پورت، مشاهده یا حذف پورت‌ها).
    """
    menu_items = [
        "1- Add Port",
        "2- Toggle Port State (Enable/Disable)",
        "3- Set Port as Trunk or Access",
        "4- View or Delete Ports",
        "5- Return to Previous Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان منو در وسط صفحه
        title = "Open vSwitch Port Management"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(menu_items):
            x = width // 2 - len(item) // 2
            y = height // 2 - len(menu_items) // 2 + idx
            if idx == current_idx:
                stdscr.addstr(y, x, item, curses.A_REVERSE | curses.A_BOLD)  # آیتم انتخاب شده
            else:
                stdscr.addstr(y, x, item)

        stdscr.refresh()
        key = stdscr.getch()

        # مدیریت کلیدها برای حرکت بین آیتم‌های منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                add_port(stdscr)
            elif current_idx == 1:
                toggle_port_state(stdscr)
            elif current_idx == 2:
                set_port_mode(stdscr)
            elif current_idx == 3:
                view_or_delete_ports(stdscr)
            elif current_idx == 4:
                return
        elif key == curses.KEY_MOUSE:
            # مدیریت کلیک ماوس روی آیتم‌ها
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        add_port(stdscr)
                    elif current_idx == 1:
                        toggle_port_state(stdscr)
                    elif current_idx == 2:
                        set_port_mode(stdscr)
                    elif current_idx == 3:
                        view_or_delete_ports(stdscr)
                    elif current_idx == 4:
                        return
                    break

def add_port(stdscr):
    """
    اضافه کردن یک پورت جدید به بریج OVS.
    در صورتی که پورت وجود نداشته باشد، از کاربر پرسیده می‌شود
    که آیا پورت مجازی ساخته شود یا خیر.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # گرفتن لیست بریج‌های موجود
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        # در صورت عدم وجود بریج، نمایش پیغام و بازگشت به منو
        stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها برای انتخاب
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {bridge}") // 2, f"{idx + 1}. {bridge}")

    # دریافت شماره بریج از کاربر
    stdscr.addstr(height // 2 + len(bridges), width // 2 - len("Enter the number of the bridge:") // 2, "Enter the number of the bridge:")
    curses.echo()
    bridge_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        bridge_idx = int(bridge_idx) - 1
        if 0 <= bridge_idx < len(bridges):
            bridge_name = bridges[bridge_idx]
        else:
            raise ValueError
    except ValueError:
        # در صورت انتخاب نامعتبر، نمایش پیغام و بازگشت
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # درخواست نام پورت از کاربر
    stdscr.addstr(height // 2 + len(bridges) + 4, width // 2 - len("Enter Port Name: ") // 2, "Enter Port Name: ")
    curses.echo()
    port_name = stdscr.getstr().decode('utf-8')
    curses.noecho()

    # بررسی وجود پورت
    port_exists = False
    try:
        result = subprocess.run(['ip', 'link', 'show', port_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            port_exists = True
    except subprocess.CalledProcessError:
        pass

    if port_exists:
        # در صورت وجود پورت، اضافه کردن آن به بریج
        try:
            subprocess.run(['sudo', 'ovs-vsctl', 'add-port', bridge_name, port_name], check=True)
            stdscr.addstr(height // 2 + len(bridges) + 6, width // 2 - len(f"Port '{port_name}' added to '{bridge_name}' successfully.") // 2, f"Port '{port_name}' added to '{bridge_name}' successfully.")
        except subprocess.CalledProcessError as e:
            stdscr.addstr(height // 2 + len(bridges) + 6, width // 2 - len(f"Failed to add port '{port_name}' to '{bridge_name}'.") // 2, f"Failed to add port '{port_name}' to '{bridge_name}'.")
    else:
        # اگر پورت وجود ندارد، از کاربر سوال شود که آیا پورت مجازی ساخته شود
        stdscr.addstr(height // 2 + len(bridges) + 6, width // 2 - len(f"Port '{port_name}' does not exist.") // 2, f"Port '{port_name}' does not exist.")
        stdscr.addstr(height // 2 + len(bridges) + 7, width // 2 - len("Do you want to create a virtual port? (y/n): ") // 2, "Do you want to create a virtual port? (y/n): ")
        key = stdscr.getch()

        if key == ord('y') or key == ord('Y'):
            # ایجاد پورت مجازی و اضافه کردن به بریج
            try:
                subprocess.run(['sudo', 'ovs-vsctl', 'add-port', bridge_name, port_name, '--', 'set', 'interface', port_name, 'type=internal'], check=True)
                stdscr.addstr(height // 2 + len(bridges) + 8, width // 2 - len(f"Virtual port '{port_name}' created and added to '{bridge_name}' successfully.") // 2, f"Virtual port '{port_name}' created and added to '{bridge_name}' successfully.")

                # فعال کردن پورت مجازی
                subprocess.run(['sudo', 'ip', 'link', 'set', port_name, 'up'], check=True)
                stdscr.addstr(height // 2 + len(bridges) + 9, width // 2 - len(f"Port '{port_name}' is now up and running.") // 2, f"Port '{port_name}' is now up and running.")
            except subprocess.CalledProcessError as e:
                stdscr.addstr(height // 2 + len(bridges) + 8, width // 2 - len(f"Failed to create virtual port '{port_name}'.") // 2, f"Failed to create virtual port '{port_name}'.")
        else:
            # اگر کاربر پورت مجازی را ایجاد نکند
            stdscr.addstr(height // 2 + len(bridges) + 8, width // 2 - len("Operation cancelled by user. Returning...") // 2, "Operation cancelled by user. Returning...")

    # پیام پایان عملیات و انتظار برای کلید فشاری
    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()

def toggle_port_state(stdscr):
    """
    تابعی برای مدیریت تغییر وضعیت پورت‌ها (فعال/غیرفعال کردن) در Open vSwitch.
    کاربر باید ابتدا بریج را انتخاب کرده، سپس پورت مربوطه را انتخاب کند.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # گرفتن لیست بریج‌های موجود
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        # اگر هیچ بریجی وجود نداشته باشد، پیام خطا نمایش داده می‌شود
        stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها برای انتخاب توسط کاربر
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {bridge}") // 2, f"{idx + 1}. {bridge}")

    # گرفتن ورودی شماره بریج از کاربر
    stdscr.addstr(height // 2 + len(bridges), width // 2 - len("Enter the number of the bridge: ") // 2, "Enter the number of the bridge: ")
    curses.echo()
    bridge_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        bridge_idx = int(bridge_idx) - 1
        if 0 <= bridge_idx < len(bridges):
            bridge_name = bridges[bridge_idx]
        else:
            raise ValueError
    except ValueError:
        # نمایش پیام خطا در صورت انتخاب نامعتبر
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # گرفتن لیست پورت‌های بریج انتخاب‌شده
    try:
        result = subprocess.run(['ovs-vsctl', 'list-ports', bridge_name], stdout=subprocess.PIPE, check=True)
        ports = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        ports = []

    if not ports:
        # اگر هیچ پورتی در بریج انتخاب‌شده وجود نداشته باشد
        stdscr.addstr(height // 2, width // 2 - len(f"No ports found for bridge {bridge_name}.") // 2, f"No ports found for bridge {bridge_name}.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست پورت‌ها برای انتخاب توسط کاربر
    stdscr.clear()
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Port:") // 2, "Select a Port:")
    for idx, port in enumerate(ports):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {port}") // 2, f"{idx + 1}. {port}")

    # دریافت شماره پورت از کاربر
    stdscr.addstr(height // 2 + len(ports), width // 2 - len("Enter the number of the port: ") // 2, "Enter the number of the port: ")
    curses.echo()
    port_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        port_idx = int(port_idx) - 1
        if 0 <= port_idx < len(ports):
            port_name = ports[port_idx]
        else:
            raise ValueError
    except ValueError:
        # پیام خطا در صورت انتخاب نامعتبر
        stdscr.addstr(height // 2 + len(ports) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # انتخاب عملیات فعال یا غیرفعال‌سازی پورت
    stdscr.clear()
    stdscr.addstr(height // 2 - 2, width // 2 - len(f"Enable or Disable '{port_name}' (e/d): ") // 2, f"Enable or Disable '{port_name}' (e/d): ")
    key = stdscr.getch()

    if key == ord('e'):
        try:
            # فعال‌سازی پورت
            subprocess.run(['sudo', 'ip', 'link', 'set', port_name, 'up'], check=True)
            stdscr.addstr(height // 2, width // 2 - len(f"Port '{port_name}' enabled successfully.") // 2, f"Port '{port_name}' enabled successfully.")
        except subprocess.CalledProcessError:
            stdscr.addstr(height // 2, width // 2 - len(f"Failed to enable port '{port_name}'.") // 2, f"Failed to enable port '{port_name}'.")
    elif key == ord('d'):
        try:
            # غیرفعال‌سازی پورت
            subprocess.run(['sudo', 'ip', 'link', 'set', port_name, 'down'], check=True)
            stdscr.addstr(height // 2, width // 2 - len(f"Port '{port_name}' disabled successfully.") // 2, f"Port '{port_name}' disabled successfully.")
        except subprocess.CalledProcessError:
            stdscr.addstr(height // 2, width // 2 - len(f"Failed to disable port '{port_name}'.") // 2, f"Failed to disable port '{port_name}'.")

    # پیام پایان عملیات و انتظار برای فشردن کلید
    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()

def set_port_mode(stdscr):
    """
    تابعی برای تنظیم حالت یک پورت در Open vSwitch به حالت ترانک یا اکسس.
    کاربر ابتدا باید بریج و سپس پورت مورد نظر را انتخاب کرده و حالت آن را مشخص کند.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # گرفتن لیست بریج‌های موجود
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        # نمایش پیام خطا در صورت عدم وجود بریج
        stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها برای انتخاب توسط کاربر
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {bridge}") // 2, f"{idx + 1}. {bridge}")

    # دریافت ورودی شماره بریج از کاربر
    stdscr.addstr(height // 2 + len(bridges), width // 2 - len("Enter the number of the bridge:") // 2, "Enter the number of the bridge:")
    curses.echo()
    bridge_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        bridge_idx = int(bridge_idx) - 1
        if 0 <= bridge_idx < len(bridges):
            bridge_name = bridges[bridge_idx]
        else:
            raise ValueError
    except ValueError:
        # نمایش پیام خطا در صورت انتخاب نامعتبر
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # گرفتن لیست پورت‌های بریج انتخاب‌شده
    try:
        result = subprocess.run(['ovs-vsctl', 'list-ports', bridge_name], stdout=subprocess.PIPE, check=True)
        ports = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        ports = []

    if not ports:
        # نمایش پیام خطا در صورت عدم وجود پورت
        stdscr.addstr(height // 2, width // 2 - len(f"No ports found for bridge {bridge_name}.") // 2, f"No ports found for bridge {bridge_name}.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست پورت‌ها برای انتخاب توسط کاربر
    stdscr.clear()
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Port:") // 2, "Select a Port:")
    for idx, port in enumerate(ports):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {port}") // 2, f"{idx + 1}. {port}")

    # دریافت ورودی شماره پورت از کاربر
    stdscr.addstr(height // 2 + len(ports), width // 2 - len("Enter the number of the port:") // 2, "Enter the number of the port:")
    curses.echo()
    port_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        port_idx = int(port_idx) - 1
        if 0 <= port_idx < len(ports):
            port_name = ports[port_idx]
        else:
            raise ValueError
    except ValueError:
        # نمایش پیام خطا در صورت انتخاب نامعتبر
        stdscr.addstr(height // 2 + len(ports) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # دریافت انتخاب کاربر برای حالت ترانک یا اکسس
    stdscr.clear()
    stdscr.addstr(height // 2 - 2, width // 2 - len(f"Set '{port_name}' as Trunk or Access (t/a): ") // 2, f"Set '{port_name}' as Trunk or Access (t/a): ")
    key = stdscr.getch()

    if key == ord('t'):
        # تنظیم پورت به حالت ترانک
        try:
            subprocess.run(['sudo', 'ovs-vsctl', 'set', 'port', port_name, 'vlan_mode=trunk'], check=True)
            stdscr.addstr(height // 2, width // 2 - len(f"Port '{port_name}' set as Trunk successfully.") // 2, f"Port '{port_name}' set as Trunk successfully.")
        except subprocess.CalledProcessError:
            stdscr.addstr(height // 2, width // 2 - len(f"Failed to set port '{port_name}' as Trunk.") // 2, f"Failed to set port '{port_name}' as Trunk.")
    elif key == ord('a'):
        # تنظیم پورت به حالت اکسس
        try:
            subprocess.run(['sudo', 'ovs-vsctl', 'set', 'port', port_name, 'vlan_mode=access'], check=True)
            stdscr.addstr(height // 2 + 2, width // 2 - len(f"Port '{port_name}' set as Access successfully.") // 2, f"Port '{port_name}' set as Access successfully.")
        except subprocess.CalledProcessError:
            stdscr.addstr(height // 2 + 2, width // 2 - len(f"Failed to set port '{port_name}' as Access.") // 2, f"Failed to set port '{port_name}' as Access.")

    # نمایش پیام پایان عملیات و انتظار برای فشردن کلید
    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()

def view_or_delete_ports(stdscr):
    """
    تابعی برای مشاهده لیست پورت‌های یک بریج و امکان حذف آن‌ها.
    کاربر ابتدا باید بریج و سپس پورت مورد نظر را انتخاب کرده و اقدام به حذف آن کند.
    """
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # دریافت لیست بریج‌های موجود
        try:
            result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
            bridges = result.stdout.decode('utf-8').splitlines()
        except subprocess.CalledProcessError:
            bridges = []

        # بررسی اینکه آیا بریجی وجود دارد یا خیر
        if not bridges:
            stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
            stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
            stdscr.refresh()
            stdscr.getch()
            return

        # نمایش لیست بریج‌ها و درخواست انتخاب بریج
        stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
        for idx, bridge in enumerate(bridges):
            stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {bridge}") // 2, f"{idx + 1}. {bridge}")

        stdscr.addstr(height // 2 + len(bridges), width // 2 - len("Enter the number of the bridge:") // 2, "Enter the number of the bridge:")
        curses.echo()
        bridge_idx = stdscr.getstr().decode('utf-8')
        curses.noecho()

        try:
            bridge_idx = int(bridge_idx) - 1
            if 0 <= bridge_idx < len(bridges):
                bridge_name = bridges[bridge_idx]
            else:
                raise ValueError
        except ValueError:
            # پیام خطا در صورت انتخاب نامعتبر
            stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
            stdscr.getch()
            return

        # دریافت لیست پورت‌های بریج انتخاب شده
        try:
            result = subprocess.run(['ovs-vsctl', 'list-ports', bridge_name], stdout=subprocess.PIPE, check=True)
            ports = result.stdout.decode('utf-8').splitlines()
        except subprocess.CalledProcessError:
            ports = []

        if not ports:
            # پیام خطا در صورت عدم وجود پورت در بریج
            stdscr.addstr(height // 2, width // 2 - len(f"No ports found for bridge {bridge_name}.") // 2, f"No ports found for bridge {bridge_name}.")
            stdscr.addstr(height // 2 + 2, width // 2 - len("Press 'q' to return.") // 2, "Press 'q' to return.")
            stdscr.refresh()
            key = stdscr.getch()
            if key == ord('q'):
                return
            return

        # نمایش لیست پورت‌ها برای حذف
        stdscr.clear()
        stdscr.addstr(height // 2 - 4, width // 2 - len("Existing Ports:") // 2, "Existing Ports:")
        for idx, port in enumerate(ports):
            stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}- {port}") // 2, f"{idx + 1}- {port}")

        stdscr.addstr(height // 2 + len(ports), width // 2 - len("Press 'd' to delete a port, or 'q' to return.") // 2, "Press 'd' to delete a port, or 'q' to return.")
        stdscr.refresh()
        key = stdscr.getch()

        if key == ord('q'):
            return
        elif key == ord('d'):
            # درخواست ورود شماره پورت برای حذف
            stdscr.addstr(height // 2 + len(ports) + 2, width // 2 - len("Enter the port number to delete: ") // 2, "Enter the port number to delete: ")
            curses.echo()
            choice = stdscr.getstr().decode('utf-8')
            curses.noecho()

            try:
                choice = int(choice) - 1
                if 0 <= choice < len(ports):
                    port_to_delete = ports[choice]

                    # درخواست تأیید کاربر برای حذف پورت
                    confirm_msg = f"Are you sure you want to delete port '{port_to_delete}'? (y/n): "
                    stdscr.addstr(height // 2 + len(ports) + 4, width // 2 - len(confirm_msg) // 2, confirm_msg)
                    key_confirm = stdscr.getch()

                    if key_confirm == ord('y'):
                        try:
                            # حذف پورت از بریج
                            subprocess.run(['sudo', 'ovs-vsctl', 'del-port', bridge_name, port_to_delete], check=True)
                            stdscr.addstr(height // 2 + len(ports) + 6, width // 2 - len(f"Port '{port_to_delete}' deleted successfully.") // 2, f"Port '{port_to_delete}' deleted successfully.")
                        except subprocess.CalledProcessError:
                            stdscr.addstr(height // 2 + len(ports) + 6, width // 2 - len(f"Failed to delete port '{port_to_delete}'.") // 2, f"Failed to delete port '{port_to_delete}'.")

                        stdscr.addstr(height // 2 + len(ports) + 8, width // 2 - len("Press any key to continue...") // 2, "Press any key to continue...")
                        stdscr.getch()
                    else:
                        stdscr.addstr(height // 2 + len(ports) + 8, width // 2 - len("Operation cancelled. Press any key to continue...") // 2, "Operation cancelled. Press any key to continue...")
                        stdscr.getch()
                else:
                    # پیام خطا در صورت انتخاب نامعتبر
                    stdscr.addstr(height // 2 + len(ports) + 7, width // 2 - len("Invalid choice. Press any key to continue...") // 2, "Invalid choice. Press any key to continue...")
                    stdscr.getch()
            except ValueError:
                # پیام خطا در صورت ورود نادرست داده‌ها
                stdscr.addstr(height // 2 + len(ports) + 7, width // 2 - len("Invalid input. Press any key to continue...") // 2, "Invalid input. Press any key to continue...")
                stdscr.getch()

