# login_dialog.py - Fenêtre de connexion centrée

import customtkinter as ctk
from tkinter import messagebox
from auth import AuthManager

def center_window(window, width, height):
    """Centre une fenêtre sur l'écran"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

class LoginDialog(ctk.CTkToplevel):
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent)
        
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        self.title("🔐 Connexion - Bibliothèque Intelligente")
        self.geometry("450x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        center_window(self, 450, 500)
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(main_frame, text="📚", font=ctk.CTkFont(size=60)).pack(pady=(0, 10))
        ctk.CTkLabel(main_frame, text="BIBLIOTHÈQUE INTELLIGENTE", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(main_frame, text="Veuillez vous connecter pour continuer",
                    font=ctk.CTkFont(size=12), text_color="#888888").pack(pady=(0, 30))
        
        form_frame = ctk.CTkFrame(main_frame, fg_color="#1e1e2e", corner_radius=15)
        form_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(form_frame, text="Nom d'utilisateur", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.entry_username = ctk.CTkEntry(form_frame, placeholder_text="Entrez votre nom d'utilisateur", height=40)
        self.entry_username.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(form_frame, text="Mot de passe", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.entry_password = ctk.CTkEntry(form_frame, placeholder_text="Entrez votre mot de passe", 
                                           show="•", height=40)
        self.entry_password.pack(fill="x", padx=20, pady=(0, 20))
        
        btn_login = ctk.CTkButton(form_frame, text="SE CONNECTER", command=self.do_login,
                                 fg_color="#2ecc71", hover_color="#27ae60", height=45,
                                 font=ctk.CTkFont(size=14, weight="bold"))
        btn_login.pack(fill="x", padx=20, pady=(0, 20))
        
        info_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a2e", corner_radius=10)
        info_frame.pack(fill="x", pady=20)
        
        info_text = """🔑 Compte par défaut :
• Nom : admin
• Mot de passe : admin123

💡 Pour ajouter des utilisateurs : 
Menu → Gestion des utilisateurs (Admin uniquement)"""
        
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=11), 
                    text_color="#888888", justify="left").pack(padx=15, pady=15)
        
        self.entry_username.bind("<Return>", lambda e: self.entry_password.focus())
        self.entry_password.bind("<Return>", lambda e: self.do_login())
    
    def do_login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        success, message = self.auth_manager.login(username, password)
        
        if success:
            messagebox.showinfo("Succès", message)
            self.on_login_success()
            self.destroy()
        else:
            messagebox.showerror("Erreur", message)
            self.entry_password.delete(0, "end")
            self.entry_password.focus()