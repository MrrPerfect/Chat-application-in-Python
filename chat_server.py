import socket
import threading
from cryptography.fernet import Fernet
from collections import defaultdict


# Server configuration
server_ip = '127.0.0.2'  # Replace with your server's IP address
server_port = 8080

# Create a socket for server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Set SO_REUSEADDR option to reuse a local socket in TIME_WAIT state
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((server_ip, server_port))
server_socket.listen(5)
print(f"Server listening on {server_ip}:{server_port}")

# Dictionary to store client sockets and their corresponding chat rooms
chat_rooms = defaultdict(list)


def handle_client(sock, chat_room_name, cipher):
    while True:
        try:
            encrypted_message = sock.recv(1024)
            if not encrypted_message:
                sock.close()
                chat_rooms[chat_room_name].remove(sock)
                break

            message = cipher.decrypt(encrypted_message).decode()

            # Broadcast the received message to all clients in the same chat room
            for client_sock in chat_rooms[chat_room_name]:
                if client_sock != sock:
                    client_sock.send(cipher.encrypt(message.encode()))
        except socket.error:
            sock.close()
            chat_rooms[chat_room_name].remove(sock)
            break


# Accept incoming client connections
while True:
    try:
        client_socket, client_address = server_socket.accept()
        # For simplicity, let's assume that the chat room name is sent by the client as the first message after connecting
        chat_room = client_socket.recv(1024).decode()

        # Generate a new key for each client and send it to them
        key = Fernet.generate_key()
        cipher_suite = Fernet(key)
        client_socket.send(key)

        chat_rooms[chat_room].append(client_socket)
        print(f"Connected with {client_address} in chat room {chat_room}")

        # Start a thread to handle the client's messages
        threading.Thread(target=handle_client, args=(client_socket, chat_room, cipher_suite)).start()
    except socket.error as e:
        print("Error accepting connection: ", e)
