import curses
import subprocess

# لیستی برای ذخیره قوانین فایروال
firewall_rules = []

def center_text(stdscr, text, row_offset=0):
    """
    نمایش متن در مرکز صفحه با امکان تنظیم فاصله از مرکز.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    text -- متنی که باید نمایش داده شود
    row_offset -- فاصله‌ای که متن از مرکز به بالا یا پایین منتقل می‌شود
    """
    height, width = stdscr.getmaxyx()  # دریافت ابعاد صفحه
    x = max(0, width // 2 - len(text) // 2)  # محاسبه مختصات افقی، اطمینان از اینکه کمتر از صفر نشود
    y = max(0, min(height - 1, height // 2 + row_offset))  # محاسبه مختصات عمودی با محدودیت در محدوده صفحه
    stdscr.addstr(y, x, text)

def apply_nft_rule(rule):
    """
    تابعی برای اجرای قوانین فایروال با استفاده از nftables.

    پارامترها:
    rule -- قانون فایروال که باید اعمال شود
    """
    try:
        # بررسی وجود جدول و زنجیره فایروال
        subprocess.run("nft list table inet filter", shell=True, check=True)
    except subprocess.CalledProcessError:
        # ایجاد جدول و زنجیره در صورت عدم وجود
        subprocess.run("nft add table inet filter", shell=True)
        subprocess.run("nft add chain inet filter input { type filter hook input priority 0; policy accept; }", shell=True)
    
    try:
        # اجرای قانون nft
        subprocess.run(f"nft {rule}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def save_firewall_rules(stdscr):
    """
    ذخیره قوانین فایروال در فایل /etc/nftables.conf برای ماندگاری پس از ریبوت.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید برای نمایش پیام‌ها
    """
    stdscr.clear()
    center_text(stdscr, "Saving current firewall rules for reboot persistence...", row_offset=-1)
    try:
        subprocess.run("nft list ruleset > /etc/nftables.conf", shell=True, check=True)
        stdscr.clear()
        center_text(stdscr, "Firewall rules saved successfully!", row_offset=-1)
    except subprocess.CalledProcessError:
        stdscr.clear()
        center_text(stdscr, "Failed to save firewall rules.", row_offset=-1)

    center_text(stdscr, "Press any key to return to the menu.", row_offset=1)
    stdscr.getch()

def list_nft_rules():
    """
    دریافت لیست قوانین موجود در nftables به همراه handle آن‌ها.

    برمی‌گرداند:
    لیستی از قوانین به همراه handle آن‌ها.
    """
    try:
        result = subprocess.run("nft --handle list chain inet filter input", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            rules = result.stdout.splitlines()
            parsed_rules = []
            for rule in rules:
                if rule.strip().startswith(('ct state', 'ip saddr')):
                    parts = rule.split(' handle ')
                    if len(parts) == 2:
                        parsed_rules.append((parts[0].strip(), parts[1].strip()))  # ذخیره قانون و handle آن
            return parsed_rules
        else:
            return []
    except subprocess.CalledProcessError:
        return []

def delete_nft_rule(rule_handle):
    """
    حذف یک قانون از nftables با استفاده از handle آن.

    پارامترها:
    rule_handle -- handle قانون برای حذف
    """
    try:
        subprocess.run(f"nft delete rule inet filter input handle {rule_handle}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def manage_firewall_rules(stdscr):
    """
    مدیریت قوانین فایروال: افزودن، نمایش و حذف قوانین.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    """
    menu_items = [
        "1- Add a New Firewall Rule", 
        "2- View and Remove Existing Rules", 
        "3- Save Rules for Reboot Persistence",  
        "4- Return to Firewall Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "Firewall Access Rules Management"
        stdscr.addstr(1, width // 2 - len(title) // 2, title, curses.A_BOLD | curses.A_UNDERLINE)

        # نمایش آیتم‌های منو
        for idx, item in enumerate(menu_items):
            row_offset = idx
            if idx == current_idx:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(height // 2 + row_offset, width // 2 - len(item) // 2, item)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                add_firewall_rule(stdscr)
            elif current_idx == 1:
                view_and_remove_firewall_rules(stdscr)
            elif current_idx == 2:
                save_firewall_rules(stdscr)
            elif current_idx == 3:
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                row_offset = idx
                item_y = height // 2 + row_offset
                item_x_start = width // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)
                
                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        add_firewall_rule(stdscr)
                    elif current_idx == 1:
                        view_and_remove_firewall_rules(stdscr)
                    elif current_idx == 2:
                        save_firewall_rules(stdscr)
                    elif current_idx == 3:
                        return

def add_firewall_rule(stdscr):
    """
    اضافه کردن قوانین جدید فایروال با استفاده از قالب‌های از پیش تعیین‌شده.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    """
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    curses.echo()
    menu_items = [
        "1- Allow Established/Related Connections",
        "2- Allow Traffic on Specific Ports",
        "3- Allow Ping (ICMP Requests)",
        "4- Return to Firewall Menu"
    ]
    current_idx = 0
    while True:
        stdscr.clear()

        # نمایش عنوان
        center_text(stdscr, "Select Firewall Rule Template", row_offset=-4)

        # نمایش گزینه‌ها
        for idx, item in enumerate(menu_items):
            row_offset = idx - len(menu_items) // 2
            if idx == current_idx:
                stdscr.addstr(curses.LINES // 2 + row_offset * 2, curses.COLS // 2 - len(item) // 2, item, curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(curses.LINES // 2 + row_offset * 2, curses.COLS // 2 - len(item) // 2, item)

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_idx = (current_idx - 1) % len(menu_items)
        elif key == curses.KEY_DOWN:
            current_idx = (current_idx + 1) % len(menu_items)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if current_idx == 0:
                rule = create_ct_state_rule(stdscr)
            elif current_idx == 1:
                rule = create_port_rule(stdscr)
            elif current_idx == 2:
                rule = create_icmp_rule(stdscr)
            elif current_idx == 3:
                return

            # اعمال قانون به فایروال
            success = apply_nft_rule(rule)
            if success:
                firewall_rules.append(rule)
                stdscr.clear()
                center_text(stdscr, f"Rule '{rule}' added and applied successfully!", row_offset=-2)
            else:
                stdscr.clear()
                center_text(stdscr, f"Failed to apply rule '{rule}'.", row_offset=-2)

            center_text(stdscr, "Press any key to return to the menu.", row_offset=2)
            stdscr.getch()
            return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                row_offset = idx - len(menu_items) // 2
                item_y = curses.LINES // 2 + row_offset * 2
                item_x_start = curses.COLS // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)

                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        rule = create_ct_state_rule(stdscr)
                    elif current_idx == 1:
                        rule = create_port_rule(stdscr)
                    elif current_idx == 2:
                        rule = create_icmp_rule(stdscr)
                    elif current_idx == 3:
                        return

def create_ct_state_rule(stdscr):
    """
    ایجاد قانونی بر اساس حالت کانکشن (ct state) برای مدیریت ترافیک.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    برمی‌گرداند:
    دستور ایجاد قانون ct state
    """
    stdscr.clear()
    center_text(stdscr, "Enter state (established/related/invalid/new):", row_offset=-1)
    state = stdscr.getstr(curses.LINES // 2, curses.COLS // 2, 20).decode('utf-8', errors='replace')
    center_text(stdscr, "Action (accept/drop/reject):", row_offset=1)
    action = stdscr.getstr(curses.LINES // 2 + 2, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    return f"add rule inet filter input ct state {state} {action}"

def create_port_rule(stdscr):
    """
    ایجاد قانون بر اساس آدرس‌های IP و پورت‌ها.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    برمی‌گرداند:
    دستور ایجاد قانون پورت
    """
    curses.echo()
    stdscr.clear()
    center_text(stdscr, "Source IP:", row_offset=-1)
    saddr = stdscr.getstr(curses.LINES // 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "Destination IP:", row_offset=1)
    daddr = stdscr.getstr(curses.LINES // 2 + 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "Protocol (tcp/udp):", row_offset=3)
    protocol = stdscr.getstr(curses.LINES // 2 + 4, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    center_text(stdscr, "Destination Port:", row_offset=5)
    dport = stdscr.getstr(curses.LINES // 2 + 6, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    center_text(stdscr, "Action (accept/reject/drop):", row_offset=7)
    action = stdscr.getstr(curses.LINES // 2 + 8, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    return f"add rule inet filter input ip saddr {saddr} ip daddr {daddr} {protocol} dport {dport} {action}"

def create_icmp_rule(stdscr):
    """
    ایجاد قانون برای مدیریت درخواست‌های Ping (ICMP).

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    برمی‌گرداند:
    دستور ایجاد قانون ICMP
    """
    curses.echo()
    stdscr.clear()
    center_text(stdscr, "Source IP:", row_offset=-1)
    saddr = stdscr.getstr(curses.LINES // 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "Destination IP:", row_offset=1)
    daddr = stdscr.getstr(curses.LINES // 2 + 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "ICMP type (echo-request/destination-unreachable):", row_offset=3)
    icmp_type = stdscr.getstr(curses.LINES // 2 + 4, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    
    if icmp_type not in ["echo-request", "destination-unreachable"]:
        stdscr.clear()
        center_text(stdscr, "Invalid ICMP type. Only 'echo-request' and 'destination-unreachable' are allowed.", row_offset=-1)
        center_text(stdscr, "Press any key to return.", row_offset=1)
        stdscr.getch()
        return ""
    
    center_text(stdscr, "Action (accept/drop):", row_offset=5)
    action = stdscr.getstr(curses.LINES // 2 + 6, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    return f"add rule inet filter input ip saddr {saddr} ip daddr {daddr} icmp type {icmp_type} {action}"

def view_and_remove_firewall_rules(stdscr):
    """
    نمایش و حذف قوانین فایروال موجود.

    پارامترها:
    stdscr -- پنجره صفحه‌کلید
    """
    stdscr.clear()
    rules = list_nft_rules()
    
    if not rules:
        center_text(stdscr, "No firewall rules available.", row_offset=-2)
        center_text(stdscr, "Press any key to return...", row_offset=2)
        stdscr.getch()
        return

    center_text(stdscr, "Current Firewall Rules:", row_offset=-4)
    
    max_display_rules = curses.LINES - 10  # تعداد قوانین قابل نمایش در یک صفحه
    current_start_idx = 0
    while True:
        stdscr.clear()
        center_text(stdscr, "Current Firewall Rules:", row_offset=-4)

        # نمایش تعداد مشخصی از قوانین
        for idx in range(current_start_idx, min(current_start_idx + max_display_rules, len(rules))):
            rule, handle = rules[idx]
            display_text = f"{idx + 1}. {rule} [Handle: {handle}]"
            center_text(stdscr, display_text, row_offset=(idx - current_start_idx) * 2)

        if len(rules) > max_display_rules:
            center_text(stdscr, "< Up/Down to scroll >", row_offset=max_display_rules * 2)

        center_text(stdscr, "Press 'q' to return or press 'Enter' to remove rule:", row_offset=(max_display_rules + 2) * 2)

        key = stdscr.getch()

        if key == curses.KEY_DOWN and current_start_idx + max_display_rules < len(rules):
            current_start_idx += 1
        elif key == curses.KEY_UP and current_start_idx > 0:
            current_start_idx -= 1
        elif key == ord('q') or key == ord('Q'):
            return
        elif key in [10, 13]:  # کلید Enter
            stdscr.clear()
            center_text(stdscr, "Enter rule number to delete:", row_offset=-2)
            curses.echo()
            input_key = stdscr.getstr(curses.LINES // 2, curses.COLS // 2 - 10, 10).decode('utf-8')

            if input_key.isdigit():
                rule_idx = int(input_key) - 1
                if 0 <= rule_idx < len(rules):
                    handle = rules[rule_idx][1]
                    success = delete_nft_rule(handle)
                    if success:
                        rules.pop(rule_idx)
                        stdscr.clear()
                        center_text(stdscr, f"Rule {rule_idx + 1} removed successfully.", row_offset=-2)
                    else:
                        stdscr.clear()
                        center_text(stdscr, f"Failed to remove rule {rule_idx + 1}.", row_offset=-2)
                    stdscr.getch()
                    return
                else:
                    center_text(stdscr, "Invalid rule number.", row_offset=2)
                    stdscr.getch()
                    return
