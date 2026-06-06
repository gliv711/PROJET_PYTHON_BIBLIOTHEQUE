# login_dialog.py - Écran de connexion

import customtkinter as ctk
from tkinter import messagebox
from styles import COLORS

def show_login_screen(parent, auth_manager):
    """Affiche l'écran de connexion"""
    # Nettoyer la fenêtre
    for widget in parent.winfo_children():
        widget.destroy()
    
    # Configurer le fond
    parent.configure(fg_color=COLORS["darker"])
    
    # Cadre central
    center_frame = ctk.CTkFrame(parent, fg_color=COLORS["light"], corner_radius=20, width=450, height=500)
    center_frame.pack(expand=True)
    center_frame.pack_propagate(False)
    
    # Contenu
    ctk.CTkLabel(center_frame, text="📚", font=ctk.CTkFont(size=60)).pack(pady=(30, 10))
    ctk.CTkLabel(center_frame, text="BIBLIOTHÈQUE INTELLIGENTE", 
                font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 5))
    ctk.CTkLabel(center_frame, text="Veuillez vous connecter",
                font=ctk.CTkFont(size=12), text_color=COLORS["text_secondary"]).pack(pady=(0, 30))
    
    form_frame = ctk.CTkFrame(center_frame, fg_color="transparent")
    form_frame.pack(padx=30, fill="x", pady=10)
    
    ctk.CTkLabel(form_frame, text="Nom d'utilisateur", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
    entry_username = ctk.CTkEntry(form_frame, placeholder_text="admin", height=40)
    entry_username.pack(fill="x", pady=(5, 15))
    
    ctk.CTkLabel(form_frame, text="Mot de passe", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
    entry_password = ctk.CTkEntry(form_frame, placeholder_text="admin123", show="•", height=40)
    entry_password.pack(fill="x", pady=(5, 20))
    
    def do_login():
        username = entry_username.get().strip()
        password = entry_password.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Vérification simple
        if username == "admin" and password == "admin123":
            messagebox.showinfo("Succès", "Connexion réussie")
            # Créer l'application principale
            from main import MainApplication
            MainApplication(parent, auth_manager)
        else:
            messagebox.showerror("Erreur", "Identifiants incorrects")
            entry_password.delete(0, "end")
            entry_password.focus()
    
    btn_login = ctk.CTkButton(form_frame, text="SE CONNECTER", command=do_login,
                             fg_color=COLORS["primary"], hover_color=COLORS["primary_dark"],
                             height=45, font=ctk.CTkFont(size=14, weight="bold"))
    btn_login.pack(fill="x", pady=(0, 20))
    
    info_frame = ctk.CTkFrame(center_frame, fg_color=COLORS["dark"], corner_radius=10)
    info_frame.pack(fill="x", padx=30, pady=20)
    
    info_text = """🔑 Compte par défaut :
• Nom : admin
• Mot de passe : admin123"""
    
    ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=11), 
                text_color=COLORS["text_secondary"], justify="left").pack(padx=15, pady=15)
    
    entry_username.bind("<Return>", lambda e: entry_password.focus())
    entry_password.bind("<Return>", lambda e: do_login())