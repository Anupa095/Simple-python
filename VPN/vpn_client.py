import socket
from cryptography.fernet import Fernet

# Ask user for shared key (given by server)
key = input("Enter shared key: ").encode()
cipher = Fernet(key)

# Connect to server
client = socket.socket()
client.connect(("127.0.0.1", 12345))  # change IP if server is remote
print("Connected to VPN server!")

while True:
    msg = input("Message: ")
    if msg.lower() in ["exit", "quit"]:
        break
    client.send(cipher.encrypt(msg.encode()))
    response = client.recv(4096)
    print("Server:", cipher.decrypt(response).decode())

client.close()
