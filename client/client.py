import socket
import threading
import customtkinter as ctk
from tkinter import messagebox

# --- הגדרות עיצוב ---
ctk.set_appearance_mode("Dark")  # מצב כהה (אפשר לשנות ל-"Light")
ctk.set_default_color_theme("blue")  # צבע הדגשה (כפתורים וכו')

# --- הגדרות רשת ---
HOST = "127.0.0.1"
PORT = 42069

class ChatClient(ctk.CTk):
    def __init__(self):
        super().__init__()

        # הגדרות חלון ראשי
        self.title("Chat Room - CustomTkinter")
        self.geometry("900x600")
        
        # משתנים לוגיים
        self.client_socket = None
        self.username = ""
        self.target_user = None # למי אנחנו שולחים הודעה כרגע
        self.running = True

        # --- בניית ה-GUI ---
        self.grid_columnconfigure(1, weight=1) # צד ימין גמיש
        self.grid_rowconfigure(0, weight=1)

        # 1. סרגל צד (רשימת משתמשים)
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Online Users", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # רשימה נגללת למשתמשים
        self.users_scrollable_frame = ctk.CTkScrollableFrame(self.sidebar_frame, label_text="Select Partner")
        self.users_scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # כפתור התנתקות (אופציונלי)
        self.disconnect_btn = ctk.CTkButton(self.sidebar_frame, text="Disconnect", command=self.on_closing, fg_color="#d63031", hover_color="#c0392b")
        self.disconnect_btn.grid(row=3, column=0, padx=20, pady=20)


        # 2. אזור הצ'אט (ראשי)
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # כותרת - עם מי מדברים
        self.target_label = ctk.CTkLabel(self.main_frame, text="Select a user to start chatting", font=ctk.CTkFont(size=18))
        self.target_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # תיבת הטקסט (היסטוריית שיחה)
        self.chat_display = ctk.CTkTextbox(self.main_frame, width=500, corner_radius=10)
        self.chat_display.grid(row=1, column=0, sticky="nsew")
        self.chat_display.configure(state="disabled") # שלא יוכלו להקליד בפנים ידנית

        # 3. אזור הקלדה ושליחה
        self.entry_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.entry_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.entry_frame.grid_columnconfigure(0, weight=1)

        self.msg_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your message...")
        self.msg_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", self.send_message) # שליחה ב-Enter

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Send ➤", width=100, command=self.send_message)
        self.send_btn.grid(row=0, column=1)

        # התחלה - התחברות לשרת
        self.connect_to_server()

    def connect_to_server(self):
        # חלונית קלט לשם משתמש
        dialog = ctk.CTkInputDialog(text="Enter your username:", title="Login")
        self.username = dialog.get_input()
        
        if not self.username:
            self.destroy() # יציאה אם לא הוכנס שם
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
            
            # הפעלת תהליכון לקבלת הודעות
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.title(f"Chat Room - Logged in as: {self.username}")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server: {e}")
            self.destroy()

    def receive_messages(self):
        """פונקציה שרצה ברקע ומקבלת מידע מהשרת"""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                message = data.decode('utf-8')

                # 1. בקשת התחברות מהשרת
                if message == "LOGIN_REQUEST":
                    self.client_socket.send(self.username.encode('utf-8'))
                
                # 2. עדכון רשימת משתמשים
                elif message.startswith("USERS_LIST:"):
                    users_str = message.split(":", 1)[1]
                    users_list = users_str.split(",") if users_str else []
                    self.update_sidebar_users(users_list)

                # 3. הודעת צ'אט רגילה (Sender:Content)
                elif ":" in message:
                    sender, content = message.split(":", 1)
                    self.append_to_chat(sender, content)

                # 4. הודעות מערכת אחרות
                else:
                    self.append_to_chat("System", message)

            except Exception as e:
                print(f"Error receiving: {e}")
                self.client_socket.close()
                break

    def update_sidebar_users(self, users):
        """מוחקת את הכפתורים הישנים ויוצרת חדשים"""
        # ניקוי הרשימה הקיימת
        for widget in self.users_scrollable_frame.winfo_children():
            widget.destroy()

        # יצירת כפתור לכל משתמש
        for user in users:
            if user != self.username: # לא להציג את עצמי
                btn = ctk.CTkButton(
                    self.users_scrollable_frame, 
                    text=user,
                    command=lambda u=user: self.select_user(u), # שימוש ב-lambda לשמירת השם
                    fg_color="transparent", 
                    border_width=2,
                    text_color=("gray10", "#DCE4EE")
                )
                btn.pack(pady=5, padx=5, fill="x")

    def select_user(self, user):
        """פונקציה שמופעלת כשלוחצים על שם ברשימה"""
        self.target_user = user
        self.target_label.configure(text=f"Chatting with: {user}", text_color="#3B8ED0")
        print(f"Selected: {user}")

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if not msg:
            return

        if not self.target_user:
            messagebox.showwarning("Warning", "Please select a user from the list first!")
            return

        # הרכבת ההודעה לפי הפרוטוקול: Target:Message
        full_packet = f"{self.target_user}:{msg}"
        
        try:
            self.client_socket.send(full_packet.encode('utf-8'))
            
            # הצגה אצלי בחלון
            self.append_to_chat("Me", msg)
            self.msg_entry.delete(0, "end") # ניקוי שדה הקלט
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send: {e}")

    def append_to_chat(self, sender, message):
        """הוספת טקסט לחלון הצ'אט"""
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"[{sender}]: {message}\n")
        self.chat_display.see("end") # גלילה אוטומטית למטה
        self.chat_display.configure(state="disabled")

    def on_closing(self):
        """סגירה מסודרת"""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        self.destroy()

if __name__ == "__main__":
    app = ChatClient()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()