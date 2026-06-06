# user_manager.py - Interface de gestion des utilisateurs

import customtkinter as ctk
from tkinter import messagebox

class UserManagerDialog(ctk.CTkToplevel):
    """Fenêtre de gestion des utilisateurs (admin uniquement)"""
    
    def __init__(self, parent, auth_manager):
        super().__init__(parent)
        
        self.auth_manager = auth_manager
        self.title("👥 Gestion des utilisateurs")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.refresh_users_list()
    
    def setup_ui(self):
        """Interface de gestion"""
        
        # En-tête
        header = ctk.CTkFrame(self, height=50, fg_color="#1a1a2e")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header, text="👥 GESTION DES UTILISATEURS", 
                    font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20)
        
        # Formulaire d'ajout
        form_frame = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=10)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="➕ AJOUTER UN UTILISATEUR", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 10))
        
        form_inner = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_inner.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(form_inner, text="Nom :").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_new_user = ctk.CTkEntry(form_inner, width=150)
        self.entry_new_user.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(form_inner, text="Mot de passe :").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_new_pass = ctk.CTkEntry(form_inner, width=150, show="•")
        self.entry_new_pass.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(form_inner, text="Rôle :").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.combo_role = ctk.CTkComboBox(form_inner, values=["user", "admin"], width=80)
        self.combo_role.set("user")
        self.combo_role.grid(row=0, column=5, padx=5, pady=5)
        
        ctk.CTkButton(form_inner, text="AJOUTER", command=self.add_user, 
                     fg_color="#2ecc71", width=80).grid(row=0, column=6, padx=10, pady=5)
        
        # Liste des utilisateurs
        list_frame = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(list_frame, text="📋 LISTE DES UTILISATEURS", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # Treeview pour la liste
        import tkinter.ttk as ttk
        self.user_tree = ttk.Treeview(list_frame, columns=("Nom", "Rôle", "Créé le"), show="headings", height=10)
        self.user_tree.heading("Nom", text="Nom d'utilisateur")
        self.user_tree.heading("Rôle", text="Rôle")
        self.user_tree.heading("Créé le", text="Date de création")
        
        self.user_tree.column("Nom", width=200)
        self.user_tree.column("Rôle", width=80)
        self.user_tree.column("Créé le", width=200)
        
        self.user_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bouton supprimer
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(btn_frame, text="🗑️ SUPPRIMER", command=self.delete_user,
                     fg_color="#e74c3c", hover_color="#c0392b", width=120).pack(side="right", padx=5)
        ctk.CTkButton(btn_frame, text="🔄 RAFRAÎCHIR", command=self.refresh_users_list,
                     fg_color="#3498db", width=120).pack(side="right", padx=5)
    
    def refresh_users_list(self):
        """Rafraîchit la liste des utilisateurs"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        for user in self.auth_manager.get_users_list():
            self.user_tree.insert("", "end", values=(user["username"], user["role"], user["created_at"]))
    
    def add_user(self):
        """Ajoute un nouvel utilisateur"""
        username = self.entry_new_user.get().strip()
        password = self.entry_new_pass.get()
        role = self.combo_role.get()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        success, message = self.auth_manager.add_user(username, password, role)
        
        if success:
            messagebox.showinfo("Succès", message)
            self.entry_new_user.delete(0, "end")
            self.entry_new_pass.delete(0, "end")
            self.refresh_users_list()
        else:
            messagebox.showerror("Erreur", message)
    
    def delete_user(self):
        """Supprime l'utilisateur sélectionné"""
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur à supprimer")
            return
        
        username = self.user_tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Confirmation", f"Supprimer l'utilisateur '{username}' ?"):
            success, message = self.auth_manager.delete_user(username)
            if success:
                messagebox.showinfo("Succès", message)
                self.refresh_users_list()
            else:
                messagebox.showerror("Erreur", message)