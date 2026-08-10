import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import sounddevice as sd
import scipy.io.wavfile
from datetime import datetime
from tkinter import ttk
from database_utils import get_cipher, init_db, log_message, log_file, log_voice, load_previous_chat, load_previous_files, load_previous_voices
import struct
import time
import os

cipher = get_cipher()

def make_circle(img):
        size = (80, 80)
        img = img.resize(size, Image.Resampling.LANCZOS).convert("RGBA")

        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)

        img.putalpha(mask)
        return img

class ChatClient:
    
    def __init__(self, root, client_name):
        self.root = root
        self.client_name = client_name
        self.current_receiver = None
        self.theme = "light"  # Default theme
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.build_gui()
        self.recording = False
        self.audio_data = None
        self.fs = 44100
        self.start_client()

    def toggle_theme(self):
        if self.theme == "light":
            self.root.configure(bg="#2e2e2e")
            self.chat_log.configure(bg="#1e1e1e", fg="white", insertbackground="white")
            self.message_entry.configure(bg="#3c3c3c", fg="white", insertbackground="white")
            self.contact_list.configure(bg="#3c3c3c", fg="white")
            self.status_label.configure(bg="#2e2e2e", fg="lightgreen")
            self.top_frame.configure(bg="#2e2e2e")
            self.dp_label.configure(bg="#2e2e2e")
            self.theme = "dark"
        else:
            self.root.configure(bg="SystemButtonFace")
            self.chat_log.configure(bg="white", fg="black", insertbackground="black")
            self.message_entry.configure(bg="white", fg="black", insertbackground="black")
            self.contact_list.configure(bg="white", fg="black")
            self.status_label.configure(bg="SystemButtonFace", fg="green")
            self.top_frame.configure(bg="SystemButtonFace")
            self.dp_label.configure(bg="SystemButtonFace")
            self.theme = "light"

    
    def build_gui(self):
        self.root.title(f"Chat Client - {self.client_name}")
        self.root.geometry("700x600")  # Default size, you can resize manually

        # === Top Frame for DP and Status ===
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side='top', fill='x', pady=5)

        # DP (Profile Picture)
        self.dp_label = tk.Label(self.top_frame)
        self.dp_label.pack(side='left', padx=10)

        # Status label
        self.status_label = tk.Label(self.top_frame, text="", fg="green", font=("Helvetica", 10))
        self.status_label.pack(side='left', padx=10)

        # === Main Frame for Contact List + Chat ===
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Contact List
        self.contact_list = tk.Listbox(self.main_frame, width=15)
        self.contact_list.insert(1, "Subhan")
        self.contact_list.insert(2, "AbdulHameed")
        self.contact_list.pack(side='left', fill='y', padx=10, pady=10)
        self.contact_list.bind('<<ListboxSelect>>', self.select_receiver)

        # Chat Log
        self.chat_log = tk.Text(self.main_frame, state='disabled', height=25, width=70, wrap='word')
        self.chat_log.pack(side='left', fill='both', expand=True, pady=10)

        # === Entry + Buttons Frame ===
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side='bottom', fill='x', pady=10)

        self.message_entry = tk.Entry(self.bottom_frame, width=40)
        self.message_entry.pack(side='left', padx=5)
        self.message_entry.bind("<Return>", lambda event: self.send_message())


        self.send_button = tk.Button(self.bottom_frame, text="Send", command=self.send_message)
        self.send_button.pack(side='left', padx=5)

        self.file_button = tk.Button(self.bottom_frame, text="Send File", command=self.send_file)
        self.file_button.pack(side='left', padx=5)

        self.start_button = tk.Button(self.bottom_frame, text="🎙️ Start", command=self.start_recording)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = tk.Button(self.bottom_frame, text="🛑 Stop & Send", command=self.stop_recording)
        self.stop_button.pack(side='left', padx=5)

        self.dark_button = tk.Button(self.bottom_frame, text="🌙 Toggle Dark Mode", command=self.toggle_theme)
        self.dark_button.pack(side='right', padx=5)

        # Emoji Picker Button
        self.emoji_button = tk.Button(self.root, text="😊", command=self.open_emoji_picker)
        self.emoji_button.pack(pady=5)

        self.progress = ttk.Progressbar(self.bottom_frame, orient='horizontal', mode='determinate', length=150)
        self.progress.pack(side='right', padx=10)

    def open_emoji_picker(self):
        # Create a new popup window
        picker = tk.Toplevel(self.root)
        picker.title("Emoji Picker")
        picker.geometry("300x200")

        emoji_frame = tk.Frame(picker)
        emoji_frame.pack(fill='both', expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(emoji_frame)
        scrollbar.pack(side='right', fill='y')

        emoji_canvas = tk.Canvas(emoji_frame, yscrollcommand=scrollbar.set)
        emoji_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=emoji_canvas.yview)

        inner_frame = tk.Frame(emoji_canvas)
        emoji_canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # Add emoji buttons (extend this list as you want!)
        emojis = [
            "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊", 
            "😍", "😘", "😗", "😙", "😚", "😋", "😜", "😝", "😛", "🤑", 
            "🤗", "🤔", "🤨", "😐", "😑", "😶", "🙄", "😏", "😣", "😥",
            "😭", "😤", "😠", "😡", "😶‍🌫️", "❤️", "💔", "🔥", "✨", "🎉",
            "👍", "👎", "👏", "🙏", "🤝", "👀", "🐶", "🐱", "🐭", "🐹"
        ]

        row, col = 0, 0
        for emoji in emojis:
            btn = tk.Button(inner_frame, text=emoji, font=("Segoe UI Emoji", 12), width=3, command=lambda e=emoji: self.insert_emoji(e, picker))
            btn.grid(row=row, column=col, padx=2, pady=2)
            col += 1
            if col > 9:
                col = 0
                row += 1

        # Fix scrolling area
        inner_frame.update_idletasks()
        emoji_canvas.config(scrollregion=emoji_canvas.bbox('all'))

    def insert_emoji(self, emoji, picker_window):
        current_text = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        self.message_entry.insert(0, current_text + emoji)
        picker_window.destroy()  # Close picker after selection

    def start_recording(self):
        if not self.current_receiver:
            messagebox.showerror("Error", "Select a contact!")
            return
        self.recording = True
        self.audio_data = sd.rec(int(30 * self.fs), samplerate=self.fs, channels=2)
        self.progress["value"] = 0
        for i in range(100):
            if not self.recording:
                break
            self.progress["value"] = i + 1
            self.root.update()
            time.sleep(0.05)

    def stop_recording(self):
        if not self.recording:
            messagebox.showerror("Error", "No audio recorded.")
            return
        self.recording = False
        sd.stop()
        sd.wait()
        timestamp = datetime.now().strftime('%H%M%S')
        #filename = f"voice_{timestamp}.wav"
        os.makedirs("voice_messages", exist_ok=True)
        filename = os.path.join("voice_messages", f"voice_{timestamp}.wav")
        recorded_samples = len(self.audio_data)
        scipy.io.wavfile.write(filename, self.fs, self.audio_data[:recorded_samples])
        
        self.client_socket.sendall(f"VOICE|{self.current_receiver}|{filename}".encode('utf-8'))
        time.sleep(0.1)

        with open(filename, "rb") as f:
            voice_data = f.read()
            self.client_socket.sendall(struct.pack('>I', len(voice_data)))  # Send size
            self.client_socket.sendall(voice_data)  # Send data

        self.update_chat(f"Voice message sent: {filename}")
        log_voice(self.client_name, self.current_receiver, filename)

    def start_client(self):
        self.client_socket.connect(('127.0.0.1', 5555))
        self.client_socket.send(self.client_name.encode('utf-8'))  # Send client name to the server

        # Start a thread to listen for incoming messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    
    def select_receiver(self, event):
        selection = self.contact_list.curselection()
        if selection:
            self.current_receiver = self.contact_list.get(selection)
            self.update_chat(f"Chat with {self.current_receiver} selected")

            # === Load and display DP ===
            possible_extensions = ['.png', '.jpg', '.jpeg']
            dp_path = None
            for ext in possible_extensions:
                path = f"dps/{self.current_receiver}{ext}"
                if os.path.exists(path):
                    dp_path = path
                    break

            if dp_path:
                try:
                    img = Image.open(dp_path)
                    img_circular = make_circle(img)
                    self.dp_img = ImageTk.PhotoImage(img_circular)
                    self.dp_label.config(image=self.dp_img)
                except Exception as e:
                    print(f"Error loading DP for {self.current_receiver}: {e}")
                    self.dp_label.config(image='')
            else:
                print(f"No DP found for {self.current_receiver}")
                self.dp_label.config(image='')
                
            # Load previous messages
            previous_messages = load_previous_chat(self.client_name, self.current_receiver)
            previous_files = load_previous_files(self.client_name, self.current_receiver)
            previous_voices = load_previous_voices(self.client_name, self.current_receiver)


            # Display previous messages
            self.chat_log.config(state='normal')
            self.chat_log.delete(1.0, tk.END)  # Clear chat before loading
            for sender, msg, timestamp in previous_messages:
                self.chat_log.insert(tk.END, f"[{timestamp}] {sender}: {msg}\n")
            for sender, fname, timestamp in previous_files:
                self.chat_log.insert(tk.END, f"[{timestamp}] {sender} sent a file: {fname}\n")
            for sender, fname, timestamp in previous_voices:
                self.chat_log.insert(tk.END, f"[{timestamp}] {sender} sent a voice message: {fname}\n")
            self.chat_log.config(state='disabled')

    def send_message(self):
        if not self.current_receiver:
            messagebox.showerror("Error", "Select a contact to chat with!")
            return

        message = self.message_entry.get()
        if not message:
            return

        self.client_socket.sendall(f"MSG|{self.current_receiver}|{message}".encode('utf-8'))
        time.sleep(0.1)
        self.update_chat(f"You: {message}")
        self.message_entry.delete(0, tk.END)

        # Log the message (sender side only)
        log_message(self.client_name, self.current_receiver, message)

    def send_file(self):
        if not self.current_receiver:
            messagebox.showerror("Error", "Select a contact to send a file to!")
            return

        file_path = filedialog.askopenfilename(title="Select a file")
        if file_path:
            filename = os.path.basename(file_path)
            self.client_socket.sendall(f"FILE|{self.current_receiver}|{filename}".encode('utf-8'))
            time.sleep(0.1)
            # Send the actual file data
            with open(file_path, "rb") as f:
                file_data = f.read()
                self.client_socket.send(file_data)

            self.update_chat(f"You sent a file: {filename}")

            folder_path = "received_files"
            os.makedirs(folder_path, exist_ok=True)

            file_path = os.path.join(folder_path, filename)

            with open(file_path, "wb") as f:
                f.write(file_data)

            # Log the file (sender side only)
            log_file(self.client_name, self.current_receiver, filename)

    def update_chat(self, message):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, message + "\n")
        self.chat_log.config(state='disabled')
        self.chat_log.see(tk.END)

    def update_contact_status(self, online_list):
        self.contact_list.delete(0, tk.END)  # Clear existing items

        all_contacts = ["Subhan", "AbdulHameed"]  # All available contacts

        for name in all_contacts:
            self.contact_list.insert(tk.END, name)
            index = self.contact_list.size() - 1  # Get current position
            if name in online_list:
                self.contact_list.itemconfig(index, {'fg': 'green'})
            else:
                self.contact_list.itemconfig(index, {'fg': 'red'})


    def receive_fixed_data(self, sock, expected_bytes):
        data = b""
        while len(data) < expected_bytes:
            try:
                part = sock.recv(expected_bytes - len(data))
                if not part:
                    raise ConnectionError("Socket closed while receiving data.")
                data += part
            except Exception as e:
                print(f"Error in receive_fixed_data: {e}")
                break
        return data


    def receive_messages(self):
        while True:
            try:
                # Step 1: read the header
                header = self.client_socket.recv(1024).decode('utf-8')

                if header.startswith("STATUS|"):
                    online_list = header.split("|")[1].split(",")
                    self.update_contact_status(online_list)

                elif header.startswith("FILE"):
                    _, sender, filename = header.split("|")
                    file_data = self.receive_fixed_data(self.client_socket)
                    # with open(f"received_{filename}", "wb") as f:
                    #     f.write(file_data)
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.update_chat(f"[{timestamp}] {sender} sent a file: {filename}")
                    log_file(sender, self.client_name, filename)

                elif header.startswith("VOICE"):
                    _, sender, fname = header.split("|")

                    # Step 2: Read the next 4 bytes (length)
                    raw_len = self.receive_fixed_data(self.client_socket, 4)
                    voice_len = struct.unpack('>I', raw_len)[0]

                    # Step 3: Read the actual voice bytes
                    voice_data = self.receive_fixed_data(self.client_socket, voice_len)

                    # Step 4: Save to file
                    # with open(f"received_{fname}", "wb") as f:
                    #     f.write(voice_data)

                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.update_chat(f"[{timestamp}] {sender} sent a voice message: {fname}")
                    log_voice(sender, self.client_name, fname)

                else:
                    self.update_chat(header)

            except Exception as e:
                print(f"Error receiving messages: {e}")
                break


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    client_name = "Moazam"
    client = ChatClient(root, client_name)
    root.mainloop()