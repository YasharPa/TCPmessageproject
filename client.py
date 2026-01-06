import socket
import threading
import customtkinter as ctk
from tkinter import messagebox
import datetime

# --- Constants & Configuration ---
# Defining constants at the top level for easy maintenance
THEME_MODE = "Dark"
COLOR_THEME = "blue"
WINDOW_SIZE = "900x600"

# Chat Bubble Colors
COLOR_SENT = "#1f6aa5"       
COLOR_RECEIVED = "#DB2929"   
COLOR_SERVER_TEXT = "#a3a3a3"

# Network Configuration
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 42069

# Apply library theme settings
ctk.set_appearance_mode(THEME_MODE)
ctk.set_default_color_theme(COLOR_THEME)

class ChatClient(ctk.CTk):
  
    
    def __init__(self):
        """Initialize the client window, state variables, and UI components."""
        super().__init__()

        # --- Window Setup ---
        self.title("Chat Room - CustomTkinter Client")
        self.geometry(WINDOW_SIZE)
        
        # --- State Management ---
        self.client_socket = None
        self.username = ""
        self.target_user = None  
        self.is_running = True   

        # --- UI Initialization ---
        self._setup_ui()
        
        # --- Connection ---
        self.after(100, self.connect_to_server)

    def _setup_ui(self):
       
        # Configure main grid layout
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(0, weight=1)

        # Sidebar (User List)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        # Sidebar Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Online Users", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Scrollable User List
        self.users_scrollable_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Select Partner")
        self.users_scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Disconnect Button
        self.disconnect_btn = ctk.CTkButton(
            self.sidebar_frame, 
            text="Disconnect", 
            command=self.on_closing, 
            fg_color="#d63031", 
            hover_color="#c0392b"
        )
        self.disconnect_btn.grid(row=3, column=0, padx=20, pady=20)

        #  Main Chat Area
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Target User Label
        self.target_label = ctk.CTkLabel(
            self.main_frame, 
            text="Select a user to start chatting", 
            font=ctk.CTkFont(size=18)
        )
        self.target_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        self.chat_area = ctk.CTkScrollableFrame(self.main_frame, corner_radius=10)
        self.chat_area.grid(row=1, column=0, sticky="nsew")
        
        # Message Input Area
        self.entry_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.entry_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.entry_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your message...")
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message) 

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Send ➤", width=100, command=self.send_message)
        self.send_btn.grid(row=0, column=1)

    def connect_to_server(self):
        dialog = ctk.CTkInputDialog(text="Enter your username:", title="Login")
        self.username = dialog.get_input()
        
        # Handle cancel or empty input
        if not self.username:
            self.destroy()
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.title(f"Chat Room - Logged in as: {self.username}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.destroy()

    def receive_messages(self):
        while self.is_running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')

                if message == "LOGIN_REQUEST":
                    self.client_socket.send(self.username.encode('utf-8'))
                
                elif message.startswith("USERS_LIST:"):
                    users_str = message.split(":", 1)[1]
                    users_list = users_str.split(",") if users_str else []
                    self.update_sidebar_users(users_list)

                elif ":" in message:
                    sender, content = message.split(":", 1)
                    
                    if sender == "System": 
                        self.display_message(content, "server")
                    else:
                        self.display_message(content, "received", sender_name=sender)

                else:
                    self.display_message(message, "server")

            except Exception as e:
                print(f"[ERROR] Receiving message: {e}")
                self.client_socket.close()
                break

    def update_sidebar_users(self, users):
        # Clear existing widgets
        for widget in self.users_scrollable_frame.winfo_children():
            widget.destroy()

        # Re-populate list
        for user in users:
            if user != self.username:
                btn = ctk.CTkButton(
                    self.users_scrollable_frame, 
                    text=user,
                    command=lambda u=user: self.select_user(u),
                    fg_color="transparent", 
                    border_width=2,
                    text_color=("gray10", "#DCE4EE")
                )
                btn.pack(pady=5, padx=5, fill="x")

    def select_user(self, user):
        self.target_user = user
        self.target_label.configure(text=f"Chatting with: {user}", text_color="#3B8ED0")

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if not msg:
            return

        if not self.target_user:
            messagebox.showwarning("Warning", "Please select a user from the list first!")
            return

        # Format: Target:Message
        full_packet = f"{self.target_user}:{msg}"
        
        try:
            self.client_socket.send(full_packet.encode('utf-8'))
            
            # Display sent message locally (Right side)
            self.display_message(msg, "sent")
            
            # Clear input
            self.msg_entry.delete(0, "end")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send: {e}")

    def display_message(self, message, msg_type, sender_name=None):
        
        # Container frame for the row (transparent) to handle alignment
        bubble_container = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        bubble_container.pack(fill="x", pady=5)

        # --- Case 1: Server Message (Centered, No Bubble) ---
        if msg_type == "server":
            lbl = ctk.CTkLabel(
                bubble_container,
                text=message,
                text_color=COLOR_SERVER_TEXT,
                font=ctk.CTkFont(size=12, slant="italic")
            )
            lbl.pack(anchor="center")
            return

        # --- Case 2: Chat Bubble (Sent/Received) ---
        
        # Determine styling based on message type
        if msg_type == "sent":
            bg_color = COLOR_SENT
            align = "e"  # East = Right
            text_align = "right"
        else: # received
            bg_color = COLOR_RECEIVED
            align = "w"  # West = Left
            text_align = "left"

        # Create the bubble frame
        bubble = ctk.CTkFrame(bubble_container, fg_color=bg_color, corner_radius=15)
        bubble.pack(anchor=align, padx=10, pady=2)

        if sender_name:
            sender_lbl = ctk.CTkLabel(
                bubble, 
                text=sender_name, 
                text_color="#a0a0a0", 
                font=ctk.CTkFont(size=10, weight="bold")
            )
            sender_lbl.pack(anchor="w", padx=10, pady=(5, 0))

        msg_lbl = ctk.CTkLabel(
            bubble, 
            text=message, 
            text_color="white",
            wraplength=350,
            justify=text_align
        )
        msg_lbl.pack(padx=12, pady=8)
        
        self.chat_area.after(10, self.chat_area._parent_canvas.yview_moveto, 1.0)

    def on_closing(self):
        self.is_running = False
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        self.destroy()

if __name__ == "__main__":
    app = ChatClient()
    # Handle window close event (X button)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()