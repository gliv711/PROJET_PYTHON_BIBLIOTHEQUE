# test_simple.py
import customtkinter as ctk

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.geometry("800x600")

menu_bar = ctk.CTkFrame(root, height=50, fg_color="#1a1a2e")
menu_bar.pack(fill="x", side="top")

nav_frame = ctk.CTkFrame(menu_bar, fg_color="transparent")
nav_frame.pack(side="left", padx=20)

# Les 3 boutons
btn1 = ctk.CTkButton(nav_frame, text="📚 CATALOGUE", width=120, fg_color="#3498db")
btn1.pack(side="left", padx=5)

btn2 = ctk.CTkButton(nav_frame, text="📊 DASHBOARD", width=120, fg_color="#9b59b6")
btn2.pack(side="left", padx=5)

btn3 = ctk.CTkButton(nav_frame, text="🤖 CHATBOT", width=120, fg_color="#2ecc71")
btn3.pack(side="left", padx=5)

# Boutons de droite
right_frame = ctk.CTkFrame(menu_bar, fg_color="transparent")
right_frame.pack(side="right", padx=20)

backup = ctk.CTkButton(right_frame, text="💾 BACKUP", width=80, fg_color="#2c3e50")
backup.pack(side="left", padx=5)

restore = ctk.CTkButton(right_frame, text="🔄 RESTORE", width=80, fg_color="#2c3e50")
restore.pack(side="left", padx=5)

logout = ctk.CTkButton(right_frame, text="🚪 DÉCONNEXION", width=100, fg_color="#e74c3c")
logout.pack(side="left", padx=10)

label = ctk.CTkLabel(right_frame, text="admin (Admin)", text_color="#2ecc71")
label.pack(side="left", padx=10)

root.mainloop()