import socket
from cryptography.fernet import Fernet

# Enter the shared key from the server
key = input("Enter shared key: ").encode()
cipher = Fernet(key)

client = socket.socket()
client.connect(("127.0.0.1", 12345))  # change IP if server is remote
print("Connected to proxy server!")

while True:
    url = input("Enter website URL (or 'quit' to exit): ")
    if url.lower() == "quit":
        break

    # Send URL encrypted
    client.send(cipher.encrypt(url.encode()))

    # Collect chunks until __END__ marker
    content = b""
    while True:
        part = client.recv(4096)
        if not part:
            break
        decrypted = cipher.decrypt(part)
        if decrypted == b"__END__":
            break
        content += decrypted

    print("\n--- Website Content (first 1000 chars) ---")
    print(content.decode(errors="ignore")[:1000])
    print("-----------------------------------------\n")

client.close()
