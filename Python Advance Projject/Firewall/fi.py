from pydivert import WinDivert
from datetime import datetime
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# =======================
# Configuration
# =======================
ALLOWED_HOSTNAMES = ["youtube.com", "www.youtube.com", "googlevideo.com"]
LOG_FILE = "firewall_log.txt"
allowed_ip_cache = set()
firewall_running = False

# =======================
# Logging function
# =======================
def log_packet(action, packet):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action}: {packet.src_addr}:{packet.src_port} -> {packet.dst_addr}:{packet.dst_port}"
    print(log_entry)
    log_box.insert(tk.END, log_entry + "\n")
    log_box.see(tk.END)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

# =======================
# Extract SNI from TLS ClientHello
# =======================
def extract_sni(tcp_payload):
    try:
        if tcp_payload[0] == 0x16:  # TLS handshake
            handshake = tcp_payload[5:]
            if handshake[0] == 0x01:  # ClientHello
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
    global firewall_running
    FILTER = "tcp.DstPort == 443 or tcp.SrcPort == 443"
    try:
        with WinDivert(FILTER) as w:
            log_box.insert(tk.END, "Firewall loop started...\n")
            while firewall_running:
                for packet in w:
                    # Allow loopback traffic
                    if packet.src_addr.startswith("127.") or packet.dst_addr.startswith("127."):
                        log_packet("ALLOWED (Loopback)", packet)
                        w.send(packet)
                        continue

                    # Outgoing HTTPS
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

                    # Incoming HTTPS
                    if packet.src_port == 443:
                        if packet.src_addr in allowed_ip_cache:
                            log_packet("ALLOWED (YouTube Response)", packet)
                            w.send(packet)
                            continue
                        log_packet("BLOCKED (Response Not YouTube)", packet)
                        continue

                    # Non-HTTPS
                    log_packet("BLOCKED (Non-HTTPS)", packet)

    except PermissionError:
        log_box.insert(tk.END, "ERROR: Run this script as Administrator.\n")
    except Exception as e:
        log_box.insert(tk.END, f"Firewall error: {str(e)}\n")
    finally:
        firewall_running = False
        status_label.config(text="Firewall is OFF", fg="red")
        log_box.insert(tk.END, "Firewall stopped.\n")

# =======================
# GUI Functions
# =======================
def start_firewall():
    global firewall_running
    if not firewall_running:
        firewall_running = True
        status_label.config(text="Firewall is ON", fg="green")
        threading.Thread(target=firewall_loop, daemon=True).start()

def stop_firewall():
    global firewall_running
    firewall_running = False
    status_label.config(text="Firewall is OFF", fg="red")

def add_domain():
    domain = simpledialog.askstring("Add Domain", "Enter domain to allow:")
    if domain:
        ALLOWED_HOSTNAMES.append(domain)
        log_box.insert(tk.END, f"Added to allowed list: {domain}\n")

# =======================
# GUI Setup
# =======================
root = tk.Tk()
root.title("YouTube Firewall")
root.geometry("700x500")

status_label = tk.Label(root, text="Firewall is OFF", fg="red", font=("Arial", 14))
status_label.pack(pady=10)

log_box = scrolledtext.ScrolledText(root, width=90, height=25)
log_box.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=10)

start_btn = tk.Button(frame, text="Start Firewall", command=start_firewall, width=20)
start_btn.grid(row=0, column=0, padx=5)

stop_btn = tk.Button(frame, text="Stop Firewall", command=stop_firewall, width=20)
stop_btn.grid(row=0, column=1, padx=5)

add_btn = tk.Button(frame, text="Add Allowed Domain", command=add_domain, width=20)
add_btn.grid(row=1, column=0, columnspan=2, pady=5)

root.mainloop()
