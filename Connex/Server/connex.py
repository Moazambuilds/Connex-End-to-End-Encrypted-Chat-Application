import socket
import threading
import struct
import time
from datetime import datetime

clients = {}
online_status = set()  # ✅ New: to track online users

# Handle each client
def handle_client(client_socket, client_name):
    print(f"Started handling client: {client_name}")
    while True:
        try:
            # Attempt to receive data
            print(f"Waiting to receive data from {client_name}...")
            data = client_socket.recv(1024).decode('utf-8')
            
            if not data:
                raise Exception(f"Client {client_name} disconnected.")

            print(f"Received data from {client_name}: {data}")
            
            # Check if it's a message or file
            if data.startswith('MSG'):
                try:
                    _, receiver, message = data.split('|', 2)
                    print(f"Message from {client_name} to {receiver}: {message}")
                except ValueError as e:
                    print(f"Error parsing message: {e}")
                    continue

                if receiver in clients:
                    clients[receiver].send(f"{client_name}: {message}".encode('utf-8'))
                else:
                    print(f"Receiver {receiver} not connected.")
                    client_socket.send("Receiver not connected.".encode('utf-8'))

            elif data.startswith('FILE'):
                try:
                    _, receiver, filename = data.split('|', 2)
                    print(f"File transfer from {client_name} to {receiver}, filename: {filename}")
                except ValueError as e:
                    print(f"Error parsing file info: {e}")
                    continue

                # ✅ Step 1: Receive file size first (4 bytes)
                raw_length = client_socket.recv(4)
                if not raw_length:
                    print("Client disconnected while sending file length.")
                    break

                file_length = struct.unpack('>I', raw_length)[0]

                # ✅ Step 2: Receive file data in chunks
                file_data = b""
                while len(file_data) < file_length:
                    chunk = client_socket.recv(min(4096, file_length - len(file_data)))
                    if not chunk:
                        break
                    file_data += chunk

                # ✅ Step 3: Send to the target receiver
                if receiver in clients:
                    print(f"Sending file '{filename}' to {receiver} (size: {len(file_data)} bytes)")
                    clients[receiver].sendall(f"FILE|{client_name}|{filename}".encode('utf-8'))
                    time.sleep(0.1)
                    clients[receiver].sendall(struct.pack('>I', len(file_data)))
                    clients[receiver].sendall(file_data)
                else:
                    print(f"Receiver {receiver} not connected.")
                    client_socket.send("Receiver not connected.".encode('utf-8'))

            elif data.startswith('VOICE'):
                try:
                    _, receiver, filename = data.split('|', 2)
                    print(f"Voice message from {client_name} to {receiver}, filename: {filename}")
                except ValueError as e:
                    print(f"Error parsing voice info: {e}")
                    continue

                # Receive voice data (read 4-byte length, then actual data)
                raw_len = client_socket.recv(4)
                if not raw_len:
                    print("Error: No length received.")
                    continue
                voice_len = struct.unpack('>I', raw_len)[0]
                voice_data = b""
                while len(voice_data) < voice_len:
                    voice_data += client_socket.recv(4096)

                # Send voice data to receiver
                if receiver in clients:
                    print(f"Sending voice '{filename}' to {receiver} (size: {len(voice_data)} bytes)")
                    clients[receiver].send(f"VOICE|{client_name}|{filename}".encode('utf-8'))  # ✅ HEADER
                    clients[receiver].sendall(struct.pack('>I', len(voice_data)))              # ✅ LENGTH
                    clients[receiver].sendall(voice_data)                                      # ✅ DATA
                else:
                    print(f"Receiver {receiver} not connected.")
                    client_socket.send("Receiver not connected.".encode('utf-8'))


        except Exception as e:
            print(f"Error: {e}")
            online_status.discard(client_name)
            broadcast_status()
            clients.pop(client_name, None)
            client_socket.close()
            print(f"Connection to {client_name} closed.")
            break

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 5555)) 
    server.listen()
    print("Server listening on port 5555...")

    while True:
        try:
            client_socket, addr = server.accept()

            client_name = client_socket.recv(1024).decode('utf-8')

            clients[client_name] = client_socket        # ✅ Correct order
            online_status.add(client_name)
            broadcast_status()

            print(f"{client_name} connected from {addr}")
            thread = threading.Thread(target=handle_client, args=(client_socket, client_name))
            thread.start()
        except Exception as e:
            print(f"Server error: {e}")

def broadcast_status():
    online = ",".join(online_status)
    for client in clients.values():
        try:
            client.send(f"STATUS|{online}".encode('utf-8'))
        except Exception as e:
            print(f"Broadcast error: {e}")


if __name__ == "__main__":
    start_server()