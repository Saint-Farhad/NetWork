import curses
import subprocess

nat_rules = []  # لیست قوانین NAT

def center_text(stdscr, text, row_offset=0):
    """ نمایش متن در مرکز صفحه """
    height, width = stdscr.getmaxyx()
    x = max(0, width // 2 - len(text) // 2)
    y = max(0, min(height - 1, height // 2 + row_offset))
    stdscr.addstr(y, x, text)

def apply_nat_rule(rule):
    """
    اجرای قوانین NAT به صورت واقعی با nftables
    در صورت عدم وجود جدول و زنجیره NAT، آن‌ها را ایجاد می‌کند.
    
    پارامترها:
    rule -- قانون NAT که باید اعمال شود
    
    برمی‌گرداند:
    True در صورت موفقیت، False در صورت عدم موفقیت
    """
    try:
        # بررسی اینکه آیا جدول NAT وجود دارد یا نه
        subprocess.run("nft list table ip nat", shell=True, check=True)
    except subprocess.CalledProcessError:
        # ایجاد جدول و زنجیره‌های NAT در صورت نیاز
        subprocess.run("nft add table ip nat", shell=True)
        subprocess.run("nft add chain ip nat prerouting { type nat hook prerouting priority -100 \; }", shell=True)
        subprocess.run("nft add chain ip nat postrouting { type nat hook postrouting priority 100 \; }", shell=True)
    
    try:
        # اعمال قانون
        subprocess.run(f"nft {rule}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def save_nat_rules(stdscr):
    """
    ذخیره قوانین NAT در فایل /etc/nftables.conf برای ماندگاری پس از ریبوت
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    stdscr.clear()
    center_text(stdscr, "Saving current NAT rules for reboot persistence...", row_offset=-1)
    try:
        subprocess.run("nft list ruleset > /etc/nftables.conf", shell=True, check=True)
        stdscr.clear()
        center_text(stdscr, "NAT rules saved successfully!", row_offset=-1)
    except subprocess.CalledProcessError:
        stdscr.clear()
        center_text(stdscr, "Failed to save NAT rules.", row_offset=-1)

    center_text(stdscr, "Press any key to return to the menu.", row_offset=1)
    stdscr.getch()

def list_nat_rules():
    """
    دریافت لیست قوانین NAT از nftables به همراه handle آن‌ها
    
    برمی‌گرداند:
    لیستی از قوانین NAT و handle آن‌ها
    """
    try:
        # گرفتن قوانین postrouting برای Masquerade
        result_post = subprocess.run("nft --handle list chain ip nat postrouting", shell=True, capture_output=True, text=True)
        post_rules = result_post.stdout.splitlines() if result_post.returncode == 0 else []
        
        # گرفتن قوانین prerouting برای DNAT
        result_pre = subprocess.run("nft --handle list chain ip nat prerouting", shell=True, capture_output=True, text=True)
        pre_rules = result_pre.stdout.splitlines() if result_pre.returncode == 0 else []

        # ترکیب و پردازش قوانین
        parsed_rules = []
        for rule in post_rules + pre_rules:
            if rule.strip().startswith(('oifname', 'ip saddr')):
                parts = rule.split(' handle ')
                if len(parts) == 2:
                    parsed_rules.append((parts[0].strip(), parts[1].strip()))  # (قانون، handle)

        return parsed_rules
    except subprocess.CalledProcessError:
        return []

def delete_nat_rule(rule_handle, is_postrouting=True):
    """
    حذف یک قانون NAT از nftables بر اساس handle آن
    
    پارامترها:
    rule_handle -- handle قانون NAT که باید حذف شود
    is_postrouting -- مشخص می‌کند که آیا قانون postrouting است یا prerouting
    برمی‌گرداند:
    True در صورت موفقیت، False در صورت عدم موفقیت
    """
    try:
        chain = "postrouting" if is_postrouting else "prerouting"
        subprocess.run(f"nft delete rule ip nat {chain} handle {rule_handle}", shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def manage_nat_rules(stdscr):
    """
    منوی مدیریت قوانین NAT
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    menu_items = [
        "1- Add a New NAT Rule", 
        "2- View and Remove Existing Rules", 
        "3- Save Rules for Reboot Persistence",
        "4- Return to NAT Menu"
    ]
    current_idx = 0
    curses.mousemask(curses.ALL_MOUSE_EVENTS)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # نمایش عنوان
        title = "NAT Rules Management"
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
        elif key in [10, 13]:
            if current_idx == 0:
                add_nat_rule(stdscr)
            elif current_idx == 1:
                view_and_remove_nat_rules(stdscr)
            elif current_idx == 2:
                save_nat_rules(stdscr)
            elif current_idx == 3:
                return
        elif key == curses.KEY_MOUSE:
            _, mx, my, _, _ = curses.getmouse()
            for idx, item in enumerate(menu_items):
                item_y = height // 2 + idx
                item_x_start = width // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)
                
                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        add_nat_rule(stdscr)
                    elif current_idx == 1:
                        view_and_remove_nat_rules(stdscr)
                    elif current_idx == 2:
                        save_nat_rules(stdscr)
                    elif current_idx == 3:
                        return

def add_nat_rule(stdscr):
    """
    اضافه کردن قانون NAT جدید
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    curses.echo()
    menu_items = [
        "1- Masquerade Rule",
        "2- DNAT Rule",
        "3- Return to NAT Menu"
    ]
    current_idx = 0
    while True:
        stdscr.clear()

        center_text(stdscr, "Select NAT Rule Template", row_offset=-4)

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
        elif key in [10, 13]:
            if current_idx == 0:
                rule = create_masquerade_rule(stdscr)
            elif current_idx == 1:
                rule = create_dnat_rule(stdscr)
            elif current_idx == 2:
                return

            # اضافه کردن و اعمال قانون NAT
            success = apply_nat_rule(rule)
            if success:
                nat_rules.append(rule)
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
                item_y = curses.LINES // 2 + (idx - len(menu_items) // 2) * 2
                item_x_start = curses.COLS // 2 - len(item) // 2
                item_x_end = item_x_start + len(item)
                
                if item_y == my and item_x_start <= mx <= item_x_end:
                    current_idx = idx
                    if current_idx == 0:
                        rule = create_masquerade_rule(stdscr)
                    elif current_idx == 1:
                        rule = create_dnat_rule(stdscr)
                    elif current_idx == 2:
                        return

def get_interfaces():
    """
    دریافت لیست اینترفیس‌های شبکه برای قوانین NAT
    
    برمی‌گرداند:
    لیستی از اینترفیس‌های موجود
    """
    try:
        result = subprocess.run("ip link | awk -F: '$0 !~ \"lo|vir|wl|^[^0-9]\" {print $2}'", 
                                shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            interfaces = result.stdout.strip().split("\n")
            return interfaces
        else:
            return []
    except subprocess.CalledProcessError:
        return []

def create_masquerade_rule(stdscr):
    """
    ساخت قانون Masquerade برای NAT
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    stdscr.clear()
    interfaces = get_interfaces()  # دریافت لیست اینترفیس‌های شبکه
    if interfaces:
        interfaces_str = ", ".join(interfaces)
        center_text(stdscr, f"Source Interface (available: {interfaces_str}):", row_offset=-1)
    else:
        center_text(stdscr, "Source Interface:", row_offset=-1)
    
    interface = stdscr.getstr(curses.LINES // 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    return f"add rule ip nat postrouting oifname {interface} masquerade"

def create_dnat_rule(stdscr):
    """
    ساخت قانون DNAT برای NAT
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    curses.echo()
    stdscr.clear()
    center_text(stdscr, "Source IP:", row_offset=-1)
    saddr = stdscr.getstr(curses.LINES // 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "Destination IP:", row_offset=1)
    daddr = stdscr.getstr(curses.LINES // 2 + 2, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    center_text(stdscr, "Destination Port:", row_offset=3)
    dport = stdscr.getstr(curses.LINES // 2 + 4, curses.COLS // 2, 10).decode('utf-8', errors='replace')
    center_text(stdscr, "New Destination IP:Port:", row_offset=5)
    dnat_to = stdscr.getstr(curses.LINES // 2 + 6, curses.COLS // 2, 30).decode('utf-8', errors='replace')
    return f"add rule ip nat prerouting ip saddr {saddr} ip daddr {daddr} tcp dport {dport} dnat to {dnat_to}"

def view_and_remove_nat_rules(stdscr):
    """
    نمایش و حذف قوانین NAT موجود
    
    پارامترها:
    stdscr -- پنجره ترمینال curses
    """
    stdscr.clear()
    
    rules = list_nat_rules()  # گرفتن لیست قوانین موجود
    
    if not rules:
        center_text(stdscr, "No NAT rules available.", row_offset=-2)
        center_text(stdscr, "Press any key to return...", row_offset=2)
        stdscr.getch()
        return

    center_text(stdscr, "Current NAT Rules:", row_offset=-4)
    
    max_display_rules = curses.LINES - 10  # تعداد قوانین قابل نمایش در یک صفحه
    current_start_idx = 0
    while True:
        stdscr.clear()
        center_text(stdscr, "Current NAT Rules:", row_offset=-4)

        # نمایش لیست قوانین NAT
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
        elif key in [10, 13]:
            stdscr.clear()
            center_text(stdscr, "Enter rule number to delete:", row_offset=-2)
            curses.echo()
            input_key = stdscr.getstr(curses.LINES // 2, curses.COLS // 2 - 10, 10).decode('utf-8')

            if input_key.isdigit():
                rule_idx = int(input_key) - 1
                if 0 <= rule_idx < len(rules):
                    handle = rules[rule_idx][1]
                    is_postrouting = "oifname" in rules[rule_idx][0]
                    success = delete_nat_rule(handle, is_postrouting)
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
