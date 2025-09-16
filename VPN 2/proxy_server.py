import socket
import requests
from cryptography.fernet import Fernet

# ---------------------------
# Generate encryption key
# ---------------------------
key = Fernet.generate_key()
cipher = Fernet(key)
print("=== VPN Proxy Server Started ===")
print("Share this key with the client to connect securely:")
print(key.decode())

# ---------------------------
# Start TCP server
# ---------------------------
server = socket.socket()
server.bind(("0.0.0.0", 12345))
server.listen(1)
print("Waiting for client connection...")

conn, addr = server.accept()
print("Client connected:", addr)

# ---------------------------
# Main loop
# ---------------------------
while True:
    data = conn.recv(8192)
    if not data:
        break

    try:
        # Decrypt URL sent by client
        url = cipher.decrypt(data).decode()
        print("Fetching:", url)

        # Fetch webpage (ignore SSL cert errors for testing)
        resp = requests.get(url, verify=False)
        content = resp.text.encode(errors="ignore")

        # Break content into small chunks (1 KB) for Fernet
        chunk_size = 1024
        for i in range(0, len(content), chunk_size):
            part = content[i:i + chunk_size]
            conn.send(cipher.encrypt(part))

        # Send end marker
        conn.send(cipher.encrypt(b"__END__"))

    except Exception as e:
        print("Error:", e)
        break

# ---------------------------
# Close connection
# ---------------------------
conn.close()
server.close()
print("Server stopped.")
