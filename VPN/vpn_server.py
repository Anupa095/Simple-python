import socket
from cryptography.fernet import Fernet

# Generate encryption key (share this with the client!)
key = Fernet.generate_key()
cipher = Fernet(key)
print("=== VPN Server Started ===")
print("Share this key with client to connect securely:")
print(key.decode())  # You’ll copy this to the client

# Create TCP server
server = socket.socket()
server.bind(("0.0.0.0", 12345))  # listen on all network interfaces
server.listen(1)
print("Waiting for client connection...")

conn, addr = server.accept()
print("Client connected:", addr)

while True:
    data = conn.recv(4096)
    if not data:
        break
    try:
        decrypted = cipher.decrypt(data).decode()
        print("Client:", decrypted)
        # send encrypted reply
        response = cipher.encrypt(f"Server got: {decrypted}".encode())
        conn.send(response)
    except Exception as e:
        print("Decryption error:", e)
        break

conn.close()
server.close()
