from pydivert import WinDivert
from datetime import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
import time
import random
import socket

# =======================
# Configuration
# =======================
ALLOWED_HOSTNAMES = ["youtube.com", "www.youtube.com", "googlevideo.com"]
LOG_FILE = "firewall_log.txt"
allowed_ip_cache = set()
firewall_running = False
windivert_handle = None
blocked_count = 0
allowed_count = 0
ip_cache = {}  # Cache for IP -> hostname

# =======================
# Function to get hostname
# =======================
def get_hostname(ip):
    if ip in ip_cache:
        return ip_cache[ip]
    try:
        hostname = socket.gethostbyaddr(ip)[0]
        ip_cache[ip] = hostname
        return hostname
    except:
        ip_cache[ip] = "Unknown"
        return "Unknown"

# =======================
# Logging function
# =======================
def log_packet(action, packet):
    global blocked_count, allowed_count
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dest_ip = packet.dst_addr
    dest_host = get_hostname(dest_ip)  # Resolve hostname
    log_entry = f"[{timestamp}] {action}: {packet.src_addr}:{packet.src_port} -> {dest_ip}:{packet.dst_port} ({dest_host})\n"
    
    log_box.configure(state="normal")
    if "BLOCKED" in action:
        log_box.insert(tk.END, log_entry, "blocked")
        blocked_count += 1
        update_counters()
        log_box.tag_config("blocked", foreground="#00FF00")  # bright green
    else:
        log_box.insert(tk.END, log_entry)
        allowed_count += 1
        update_counters()
    log_box.see(tk.END)
    log_box.configure(state="disabled")
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

# =======================
# Extract SNI from TLS ClientHello
# =======================
def extract_sni(tcp_payload):
    try:
        if tcp_payload[0] == 0x16:
            handshake = tcp_payload[5:]
            if handshake[0] == 0x01:
                ptr = 43
                if ptr + 5 >= len(handshake):
                    return None
                while ptr + 5 < len(handshake):
                    name_type = handshake[ptr]
                    name_len = (handshake[ptr+1] << 8) | handshake[ptr+2]
                    server_name = handshake[ptr+3:ptr+3+name_len].decode(errors='ignore')
                    return server_name.lower()
    except Exception:
        return None
    return None

# =======================
# Firewall packet loop
# =======================
def firewall_loop():
    global firewall_running, windivert_handle
    FILTER = "tcp.DstPort == 443 or tcp.SrcPort == 443"
    
    try:
        with WinDivert(FILTER) as w:
            windivert_handle = w
            log_box.configure(state="normal")
            log_box.insert(tk.END, "Firewall loop started...\n")
            log_box.see(tk.END)
            log_box.configure(state="disabled")
            
            while firewall_running:
                for packet in w:
                    if not firewall_running:
                        break
                    
                    # Allow loopback traffic
                    if packet.src_addr.startswith("127.") or packet.dst_addr.startswith("127."):
                        log_packet("ALLOWED (Loopback)", packet)
                        w.send(packet)
                        continue

                    # Check outgoing HTTPS
                    if packet.dst_port == 443:
                        if packet.tcp and len(packet.tcp.payload) > 0:
                            sni = extract_sni(packet.tcp.payload)
                            if sni and any(host in sni for host in ALLOWED_HOSTNAMES):
                                allowed_ip_cache.add(packet.dst_addr)
                                log_packet("ALLOWED (YouTube TLS)", packet)
                                w.send(packet)
                                continue
                        if packet.dst_addr in allowed_ip_cache:
                            log_packet("ALLOWED (Cached IP)", packet)
                            w.send(packet)
                            continue
                        log_packet("BLOCKED (Not YouTube)", packet)
                        continue

                    # Check incoming HTTPS
                    if packet.src_port == 443:
                        if packet.src_addr in allowed_ip_cache:
                            log_packet("ALLOWED (YouTube Response)", packet)
                            w.send(packet)
                            continue
                        log_packet("BLOCKED (Response Not YouTube)", packet)
                        continue

                    log_packet("BLOCKED (Non-HTTPS)", packet)
                    
                    if not firewall_running:
                        break
                break
    except PermissionError:
        log_box.configure(state="normal")
        log_box.insert(tk.END, "ERROR: Run this script as Administrator.\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")
    except Exception as e:
        log_box.configure(state="normal")
        log_box.insert(tk.END, f"Firewall error: {str(e)}\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")
    finally:
        windivert_handle = None
        firewall_running = False
        status_label.config(text="Firewall is OFF", foreground="red")
        log_box.configure(state="normal")
        log_box.insert(tk.END, "Firewall stopped.\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")

# =======================
# GUI Functions
# =======================
def start_firewall():
    global firewall_running
    if not firewall_running:
        firewall_running = True
        status_label.config(text="Firewall is ON", foreground="green")
        threading.Thread(target=firewall_loop, daemon=True).start()

def stop_firewall():
    global firewall_running
    if firewall_running:
        firewall_running = False
        status_label.config(text="Firewall is OFF", foreground="red")
        log_box.configure(state="normal")
        log_box.insert(tk.END, "Stopping firewall...\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")

def add_domain():
    domain = domain_entry.get().strip()
    if domain:
        if domain not in ALLOWED_HOSTNAMES:
            ALLOWED_HOSTNAMES.append(domain)
            log_box.configure(state="normal")
            log_box.insert(tk.END, f"Added to allowed list: {domain}\n")
            log_box.see(tk.END)
            log_box.configure(state="disabled")
            domain_entry.delete(0, tk.END)
            update_domain_list()
        else:
            log_box.configure(state="normal")
            log_box.insert(tk.END, f"Domain already in allowed list: {domain}\n")
            log_box.see(tk.END)
            log_box.configure(state="disabled")
    else:
        log_box.configure(state="normal")
        log_box.insert(tk.END, "Please enter a domain name.\n")
        log_box.see(tk.END)
        log_box.configure(state="disabled")

def remove_domain():
    selected = domain_listbox.curselection()
    if selected:
        domain = domain_listbox.get(selected[0])
        if domain in ALLOWED_HOSTNAMES:
            ALLOWED_HOSTNAMES.remove(domain)
            log_box.configure(state="normal")
            log_box.insert(tk.END, f"Removed from allowed list: {domain}\n")
            log_box.see(tk.END)
            log_box.configure(state="disabled")
            update_domain_list()
            allowed_ip_cache.clear()

def update_domain_list():
    domain_listbox.delete(0, tk.END)
    for domain in ALLOWED_HOSTNAMES:
        domain_listbox.insert(tk.END, domain)

def update_counters():
    allowed_label.config(text=f"Allowed: {allowed_count}")
    blocked_label.config(text=f"Blocked: {blocked_count}")

def on_enter_key(event):
    add_domain()

def on_closing():
    global firewall_running
    if firewall_running:
        stop_firewall()
        time.sleep(1)
    root.destroy()

# =======================
# Matrix-style animation
# =======================
def matrix_effect():
    for _ in range(5):
        x = random.randint(0, root.winfo_width())
        y = 0
        color = "#00FF00"
        canvas.create_text(x, y, text=random.choice("01"), fill=color, font=("Consolas", 10, "bold"), tags="matrix")
    for item in canvas.find_withtag("matrix"):
        canvas.move(item, 0, 5)
        if canvas.coords(item)[1] > root.winfo_height():
            canvas.delete(item)
    root.after(50, matrix_effect)

# =======================
# GUI Setup
# =======================
root = tk.Tk()
root.title("Firewall - Terminal")
root.geometry("1000x700")
root.configure(bg="gray")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Matrix background
canvas = tk.Canvas(root, width=1000, height=700, bg="black")
canvas.place(x=0, y=0, relwidth=1, relheight=1)
matrix_effect()

frame = tk.Frame(root, bg="gray")
frame.place(relwidth=1, relheight=1)

title_label = tk.Label(frame, text="Network Firewall Manager", font=("Consolas", 20, "bold"), bg="gray", fg="white")
title_label.pack(pady=10)

status_label = tk.Label(frame, text="Firewall is OFF", font=("Consolas", 14, "bold"), bg="gray", fg="red")
status_label.pack(pady=5)

# Counters
counter_frame = tk.Frame(frame, bg="gray")
counter_frame.pack(pady=5)
allowed_label = tk.Label(counter_frame, text="Allowed: 0", font=("Consolas", 12), bg="gray", fg="white")
allowed_label.pack(side="left", padx=10)
blocked_label = tk.Label(counter_frame, text="Blocked: 0", font=("Consolas", 12), bg="gray", fg="#00FF00")
blocked_label.pack(side="left", padx=10)

# Domain management
domain_frame = tk.Frame(frame, bg="gray")
domain_frame.pack(pady=10, fill="x", padx=20)

input_frame = tk.Frame(domain_frame, bg="gray")
input_frame.pack(fill="x", pady=(0, 10))

tk.Label(input_frame, text="Add Domain:", font=("Consolas", 12, "bold"), bg="gray", fg="white").pack(side="left")

domain_entry = tk.Entry(input_frame, font=("Consolas", 12), width=30, bg="lightgray", fg="black", insertbackground="black")
domain_entry.pack(side="left", padx=(10, 5), fill="x", expand=True)
domain_entry.bind("<Return>", on_enter_key)

add_domain_btn = tk.Button(input_frame, text="Add", command=add_domain, font=("Consolas", 10),
                          bg="green", fg="white", relief="flat", padx=15)
add_domain_btn.pack(side="right", padx=(5, 0))

list_frame = tk.Frame(domain_frame, bg="gray")
list_frame.pack(fill="both", expand=True)

tk.Label(list_frame, text="Allowed Domains:", font=("Consolas", 12, "bold"), bg="gray", fg="white").pack(anchor="w")

listbox_frame = tk.Frame(list_frame, bg="gray")
listbox_frame.pack(fill="both", expand=True, pady=(5, 0))

domain_listbox = tk.Listbox(listbox_frame, height=5, font=("Consolas", 10), bg="lightgray", fg="black",
                           selectbackground="green", selectforeground="white")
domain_listbox.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(listbox_frame)
scrollbar.pack(side="right", fill="y")
domain_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=domain_listbox.yview)

remove_btn = tk.Button(list_frame, text="Remove Selected", command=remove_domain, font=("Consolas", 10),
                      bg="red", fg="white", relief="flat", padx=15)
remove_btn.pack(pady=(5, 10))

# Log box
log_box = scrolledtext.ScrolledText(frame, width=100, height=15, bg="black", fg="white",
                                   font=("Consolas", 10, "bold"), insertbackground="white")
log_box.pack(pady=10, fill="both", expand=True)
log_box.configure(state="disabled")

# Buttons frame
btn_frame = tk.Frame(frame, bg="gray")
btn_frame.pack(pady=10)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Consolas", 12), padding=6, relief="flat")
style.map("TButton",
          foreground=[('active', 'white')],
          background=[('active', 'green')])

start_btn = ttk.Button(btn_frame, text="Start Firewall", command=start_firewall, width=20)
start_btn.grid(row=0, column=0, padx=10, pady=5)

stop_btn = ttk.Button(btn_frame, text="Stop Firewall", command=stop_firewall, width=20)
stop_btn.grid(row=0, column=1, padx=10, pady=5)

root.after(100, update_domain_list)
root.mainloop()
