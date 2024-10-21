import curses
import subprocess

def manage_ovs_vlans(stdscr):
    """
    مدیریت VLANها در Open vSwitch. این تابع یک منوی TUI را ارائه می‌دهد
    که کاربر می‌تواند گزینه‌های مختلف مربوط به مدیریت VLAN را انتخاب کند.
    """
    menu_items = [
        "1- Create VLAN Interface",      # ایجاد اینترفیس VLAN
        "2- Set IP for VLAN Interface",  # تنظیم IP برای اینترفیس VLAN
        "3- Set VLAN for Trunk Port",    # تنظیم VLAN برای پورت ترانک
        "4- Delete VLAN Interface",      # حذف اینترفیس VLAN
        "5- Return to Previous Menu"     # بازگشت به منوی قبلی
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان منوی VLAN
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

        # مدیریت انتخاب کاربر در منو
        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key in [10, 13]:  # Enter key
            if current_idx == 0:
                create_vlan_interface(stdscr)
            elif current_idx == 1:
                set_ip_for_vlan(stdscr)
            elif current_idx == 2:
                set_vlan_for_trunk(stdscr)
            elif current_idx == 3:
                delete_vlan_interface(stdscr)
            elif current_idx == 4:
                return  # بازگشت به منوی قبلی
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                x = width // 2 - len(item) // 2
                y = height // 2 - len(menu_items) // 2 + idx
                if y == my and x <= mx <= x + len(item):
                    current_idx = idx
                    if current_idx == 0:
                        create_vlan_interface(stdscr)
                    elif current_idx == 1:
                        set_ip_for_vlan(stdscr)
                    elif current_idx == 2:
                        set_vlan_for_trunk(stdscr)
                    elif current_idx == 3:
                        delete_vlan_interface(stdscr)
                    elif current_idx == 4:
                        return
                    break

def create_vlan_interface(stdscr):
    """
    ایجاد اینترفیس VLAN در Open vSwitch. این تابع از کاربر نام بریج و شماره VLAN
    را دریافت کرده و اینترفیس VLAN مربوطه را ایجاد می‌کند.
    """
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # دریافت لیست بریج‌های موجود
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        # اگر بریجی موجود نباشد، پیام نمایش داده می‌شود
        stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها برای انتخاب
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {bridge}") // 2, f"{idx + 1}. {bridge}")

    # دریافت شماره بریج انتخابی
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
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # دریافت شماره VLAN
    stdscr.addstr(height // 2 + len(bridges) + 4, width // 2 - len("Enter VLAN ID: ") // 2, "Enter VLAN ID: ")
    curses.echo()
    vlan_id = stdscr.getstr().decode('utf-8')
    curses.noecho()

    # ایجاد اینترفیس VLAN در OVS
    try:
        subprocess.run(['sudo', 'ovs-vsctl', 'add-port', bridge_name, f"{bridge_name}.{vlan_id}", '--', 'set', 'interface', f"{bridge_name}.{vlan_id}", 'type=internal'], check=True)
        stdscr.addstr(height // 2 + len(bridges) + 6, width // 2 - len(f"VLAN interface {bridge_name}.{vlan_id} created successfully.") // 2, f"VLAN interface {bridge_name}.{vlan_id} created successfully.")

        # فعال کردن اینترفیس VLAN
        subprocess.run(['sudo', 'ip', 'link', 'set', f"{bridge_name}.{vlan_id}", 'up'], check=True)
        stdscr.addstr(height // 2 + len(bridges) + 7, width // 2 - len(f"VLAN interface {bridge_name}.{vlan_id} is now up.") // 2, f"VLAN interface {bridge_name}.{vlan_id} is now up.")
    except subprocess.CalledProcessError:
        stdscr.addstr(height // 2 + len(bridges) + 6, width // 2 - len("Failed to create VLAN interface.") // 2, "Failed to create VLAN interface.")

    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()


def set_ip_for_vlan(stdscr):
    """تنظیم IP برای اینترفیس VLAN با نمایش لیست اینترفیس‌های موجود"""
    
    stdscr.clear()
    height, width = stdscr.getmaxyx()

    # دریافت لیست اینترفیس‌های VLAN موجود
    try:
        result = subprocess.run(['ip', 'link', 'show'], stdout=subprocess.PIPE, check=True)
        interfaces = result.stdout.decode('utf-8').splitlines()

        # فیلتر کردن اینترفیس‌هایی که به شکل bridge_name.VLAN_ID هستند
        vlan_interfaces = [line.split(': ')[1] for line in interfaces if len(line.split(': ')) > 1 and '.' in line.split(': ')[1]]
    except subprocess.CalledProcessError:
        vlan_interfaces = []

    if not vlan_interfaces:
        # در صورتی که اینترفیسی وجود نداشته باشد
        stdscr.addstr(height // 2, width // 2 - len("No VLAN interfaces found.") // 2, "No VLAN interfaces found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست اینترفیس‌های VLAN
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a VLAN Interface:") // 2, "Select a VLAN Interface:")
    for idx, vlan_interface in enumerate(vlan_interfaces):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {vlan_interface}") // 2, f"{idx + 1}. {vlan_interface}")

    stdscr.addstr(height // 2 + len(vlan_interfaces), width // 2 - len("Enter the number of the VLAN interface:") // 2, "Enter the number of the VLAN interface:")
    curses.echo()
    vlan_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        vlan_idx = int(vlan_idx) - 1
        if 0 <= vlan_idx < len(vlan_interfaces):
            vlan_interface = vlan_interfaces[vlan_idx]
        else:
            raise ValueError
    except ValueError:
        stdscr.addstr(height // 2 + len(vlan_interfaces) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # درخواست آدرس IP از کاربر
    stdscr.addstr(height // 2 + len(vlan_interfaces) + 4, width // 2 - len("Enter IP Address (CIDR): ") // 2, "Enter IP Address (CIDR): ")
    curses.echo()
    ip_address = stdscr.getstr().decode('utf-8')
    curses.noecho()

    # تنظیم IP روی اینترفیس VLAN
    try:
        subprocess.run(['sudo', 'ip', 'addr', 'add', ip_address, 'dev', vlan_interface], check=True)
        stdscr.addstr(height // 2 + len(vlan_interfaces) + 6, width // 2 - len(f"IP {ip_address} set successfully on {vlan_interface}.") // 2, f"IP {ip_address} set successfully on {vlan_interface}.")
    except subprocess.CalledProcessError:
        stdscr.addstr(height // 2 + len(vlan_interfaces) + 6, width // 2 - len(f"Failed to set IP {ip_address} on {vlan_interface}.") // 2, f"Failed to set IP {ip_address} on {vlan_interface}.")

    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()

def set_vlan_for_trunk(stdscr):
    """تنظیم VLAN برای پورت‌های ترانک"""
    
    # دریافت لیست بریج‌ها
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        stdscr.addstr(2, 2, "No bridges found.")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height // 2 - len(bridges) - 2, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")

    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - len(bridges) + idx, width // 2 - len(f"{idx + 1}- {bridge}") // 2, f"{idx + 1}- {bridge}")

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
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # دریافت لیست پورت‌ها و فیلتر کردن فقط اینترفیس‌های VLAN
    try:
        result = subprocess.run(['ovs-vsctl', 'list-ports', bridge_name], stdout=subprocess.PIPE, check=True)
        ports = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        ports = []

    vlan_ports = [port for port in ports if '.' in port]

    if not vlan_ports:
        stdscr.addstr(2, 2, "No VLAN interfaces found for the selected bridge.")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست پورت‌های VLAN با امکان انتخاب چندگانه
    stdscr.clear()
    stdscr.addstr(height // 2 - len(vlan_ports) - 2, width // 2 - len("Select VLANs (use comma for multiple selections):") // 2, "Select VLANs (use comma for multiple selections):")
    
    for idx, port in enumerate(vlan_ports):
        stdscr.addstr(height // 2 - len(vlan_ports) + idx, width // 2 - len(f"{idx + 1}- {port}") // 2, f"{idx + 1}- {port}")

    stdscr.addstr(height // 2 + len(vlan_ports), width // 2 - len("Enter the numbers of the VLANs (e.g. 1,2,3):") // 2, "Enter the numbers of the VLANs (e.g. 1,2,3):")
    curses.echo()
    vlan_selection = stdscr.getstr().decode('utf-8').strip()
    curses.noecho()

    try:
        selected_indices = [int(i) - 1 for i in vlan_selection.split(',') if 0 <= int(i) - 1 < len(vlan_ports)]
        if not selected_indices:
            raise ValueError
        selected_vlans = [vlan_ports[i] for i in selected_indices]
    except ValueError:
        stdscr.addstr(height // 2 + len(vlan_ports) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # تنظیم VLANها به عنوان ترانک برای پورت انتخاب شده
    try:
        vlan_ids = ','.join([v.split('.')[-1] for v in selected_vlans])
        subprocess.run(['sudo', 'ovs-vsctl', 'set', 'port', bridge_name, f'trunks={vlan_ids}'], check=True)

        # نمایش پیام موفقیت
        stdscr.clear()
        stdscr.addstr(height // 2, width // 2 - len(f"VLANs {vlan_ids} set as trunk on port {bridge_name}.") // 2, f"VLANs {vlan_ids} set as trunk on port {bridge_name}.")
    except subprocess.CalledProcessError:
        stdscr.clear()
        stdscr.addstr(height // 2, width // 2 - len("Failed to set VLANs as trunk.") // 2, "Failed to set VLANs as trunk.")

    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()


def delete_vlan_interface(stdscr):
    """حذف اینترفیس VLAN"""
    stdscr.clear()  # پاک کردن صفحه در ابتدای تابع
    height, width = stdscr.getmaxyx()

    # دریافت لیست بریج‌ها
    try:
        result = subprocess.run(['ovs-vsctl', 'list-br'], stdout=subprocess.PIPE, check=True)
        bridges = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        bridges = []

    if not bridges:
        # نمایش پیام در صورت عدم وجود بریج‌ها
        stdscr.addstr(height // 2, width // 2 - len("No bridges found.") // 2, "No bridges found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست بریج‌ها
    stdscr.clear()
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a Bridge:") // 2, "Select a Bridge:")
    for idx, bridge in enumerate(bridges):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}- {bridge}") // 2, f"{idx + 1}- {bridge}")

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
        # مدیریت ورودی اشتباه
        stdscr.addstr(height // 2 + len(bridges) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # دریافت لیست پورت‌ها برای بریج انتخاب شده
    try:
        result = subprocess.run(['ovs-vsctl', 'list-ports', bridge_name], stdout=subprocess.PIPE, check=True)
        ports = result.stdout.decode('utf-8').splitlines()
    except subprocess.CalledProcessError:
        ports = []

    # فیلتر کردن اینترفیس‌های VLAN (پورت‌هایی که شامل '.' هستند)
    vlan_interfaces = [port for port in ports if '.' in port]

    if not vlan_interfaces:
        # نمایش پیام در صورت عدم وجود اینترفیس VLAN
        stdscr.clear()
        stdscr.addstr(height // 2, width // 2 - len("No VLAN interfaces found.") // 2, "No VLAN interfaces found.")
        stdscr.addstr(height // 2 + 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
        return

    # نمایش لیست اینترفیس‌های VLAN
    stdscr.clear()
    stdscr.addstr(height // 2 - 4, width // 2 - len("Select a VLAN Interface to delete:") // 2, "Select a VLAN Interface to delete:")
    for idx, iface in enumerate(vlan_interfaces):
        stdscr.addstr(height // 2 - 2 + idx, width // 2 - len(f"{idx + 1}. {iface}") // 2, f"{idx + 1}. {iface}")

    stdscr.addstr(height // 2 + len(vlan_interfaces), width // 2 - len("Enter the number of the VLAN interface:") // 2, "Enter the number of the VLAN interface:")
    curses.echo()
    iface_idx = stdscr.getstr().decode('utf-8')
    curses.noecho()

    try:
        iface_idx = int(iface_idx) - 1
        if 0 <= iface_idx < len(vlan_interfaces):
            vlan_iface = vlan_interfaces[iface_idx]
        else:
            raise ValueError
    except ValueError:
        # مدیریت ورودی اشتباه
        stdscr.addstr(height // 2 + len(vlan_interfaces) + 2, width // 2 - len("Invalid selection. Press any key to return...") // 2, "Invalid selection. Press any key to return...")
        stdscr.getch()
        return

    # درخواست تأیید حذف اینترفیس VLAN
    stdscr.clear()
    stdscr.addstr(height // 2, width // 2 - len(f"Are you sure you want to delete {vlan_iface}? (y/n):") // 2, f"Are you sure you want to delete {vlan_iface}? (y/n):")
    key_confirm = stdscr.getch()

    if key_confirm == ord('y'):
        try:
            # حذف اینترفیس VLAN
            subprocess.run(['sudo', 'ovs-vsctl', 'del-port', bridge_name, vlan_iface], check=True)
            stdscr.addstr(height // 2 + 2, width // 2 - len(f"VLAN interface {vlan_iface} deleted successfully.") // 2, f"VLAN interface {vlan_iface} deleted successfully.")
        except subprocess.CalledProcessError:
            stdscr.addstr(height // 2 + 2, width // 2 - len(f"Failed to delete VLAN interface {vlan_iface}.") // 2, f"Failed to delete VLAN interface {vlan_iface}.")
    else:
        return

    stdscr.addstr(height - 2, width // 2 - len("Press any key to return...") // 2, "Press any key to return...")
    stdscr.getch()