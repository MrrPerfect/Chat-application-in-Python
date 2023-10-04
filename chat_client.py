import socket
import tkinter as tk
from tkinter import scrolledtext
from cryptography.fernet import Fernet


def receive_messages(sock, txt_area, cipher):
    while True:
        try:
            encrypted_message = sock.recv(1024)
            message = cipher.decrypt(encrypted_message).decode()
            txt_area.insert(tk.END, "\nReceived: " + message)
        except Exception as local_e:
            print("Error receiving message: ", local_e)
            break


def send_message(sock, entry_field, cipher):
    try:
        if cipher is None:
            raise Exception("No connection to server")
        message = entry_field.get()
        encrypted_message = cipher.encrypt(message.encode())
        sock.send(encrypted_message)
        entry_field.delete(0, tk.END)
    except Exception as local_e:
        print("Error sending message: ", local_e)


def home_page():
    for widget in window.winfo_children():
        widget.destroy()
    tk.Label(window, text="Welcome!").pack()
    tk.Button(window, text="Go to chats", command=chat_list).pack()


def chat_list():
    for widget in window.winfo_children():
        widget.destroy()
    tk.Label(window, text="Chats:").pack()
    listbox = tk.Listbox(window)
    listbox.pack()
    for i in range(10):
        listbox.insert(tk.END, "Chat " + str(i+1))
    tk.Button(window, text="Open chat", command=lambda: chat_page(listbox.get(tk.ANCHOR))).pack()


def chat_page(chat_name):
    global txt
    global entry
    for widget in window.winfo_children():
        widget.destroy()
    tk.Label(window, text="Chat with " + chat_name).pack()
    txt = scrolledtext.ScrolledText(window)
    txt.pack()
    entry = tk.Entry(window)
    entry.pack()
    tk.Button(window, text="Send", command=lambda: send_message(client_socket, entry, cipher_suite)).pack()

# Server configuration


server_ip = '127.0.0.1'  # Replace with your server's actual IP address
server_port = 8080

try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Encryption key (this should be the same as the server's key!)
    key = client_socket.recv(1024).decode()
    key = key.encode()  # Encode the key into bytes
    cipher_suite = Fernet(key)

except Exception as global_e:
    print("Error connecting to server: ", global_e)
    cipher_suite = None  # Set cipher_suite to None if connection fails

window = tk.Tk()
window.title("Chat Client")

txt = scrolledtext.ScrolledText(window)
txt.pack()

entry = tk.Entry(window)
entry.pack()

button = tk.Button(window, text="Send", command=lambda: send_message(client_socket, entry, cipher_suite))
button.pack()

home_page()

window.mainloop()
