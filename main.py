# main.py - Version avec taille fixe pour voir la barre de menu

import customtkinter as ctk
from navigation_manager import NavigationManager
from views import CatalogueView, DashboardView, ChatbotView
from auth import AuthManager
from styles import COLORS
from tkinter import messagebox

class MainApplication:
    def __init__(self, parent, auth_manager):
        self.parent = parent
        self.auth_manager = auth_manager
        
        # Nettoyer la fenêtre
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Configurer la fenêtre - TAILLE FIXE au lieu de plein écran
        self.parent.title("📚 Bibliothèque Intelligente")
        self.parent.geometry("1300x800")  # Taille fixe
        
        # Créer le gestionnaire de navigation
        self.nav_manager = NavigationManager(self.parent, self.auth_manager)
        
        # Créer le menu principal (après nav_manager)
        self.create_main_menu()
        
        # Naviguer vers le catalogue par défaut
        self.nav_manager.navigate_to(CatalogueView)
    
    def create_main_menu(self):
        """Crée le menu principal avec tous les boutons"""
        menu_bar = ctk.CTkFrame(self.parent, height=50, fg_color=COLORS["dark"])
        menu_bar.pack(fill="x", side="top")
        menu_bar.pack_propagate(False)
        
        # Logo
        ctk.CTkLabel(menu_bar, text="📚", font=ctk.CTkFont(size=24)).pack(side="left", padx=20)
        
        # ===== BOUTONS DE NAVIGATION =====
        nav_frame = ctk.CTkFrame(menu_bar, fg_color="transparent")
        nav_frame.pack(side="left", padx=10)
        
        # Catalogue
        btn_catalogue = ctk.CTkButton(
            nav_frame, 
            text="📚 CATALOGUE", 
            command=lambda: self.nav_manager.navigate_to(CatalogueView),
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_dark"],
            height=35,
            width=120
        )
        btn_catalogue.pack(side="left", padx=3)
        
        # Dashboard
        btn_dashboard = ctk.CTkButton(
            nav_frame, 
            text="📊 DASHBOARD", 
            command=lambda: self.nav_manager.navigate_to(DashboardView),
            fg_color=COLORS["info"],
            hover_color=COLORS["info_dark"],
            height=35,
            width=120
        )
        btn_dashboard.pack(side="left", padx=3)
        
        # Chatbot
        btn_chatbot = ctk.CTkButton(
            nav_frame, 
            text="🤖 CHATBOT", 
            command=lambda: self.nav_manager.navigate_to(ChatbotView),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            height=35,
            width=120
        )
        btn_chatbot.pack(side="left", padx=3)
        
        # ===== BOUTONS DE DROITE =====
        right_frame = ctk.CTkFrame(menu_bar, fg_color="transparent")
        right_frame.pack(side="right", padx=10)
        
        # BACKUP
        backup_btn = ctk.CTkButton(
            right_frame, 
            text="💾 BACKUP", 
            command=self.faire_backup,
            fg_color=COLORS["dark"],
            hover_color="#2c3e50",
            height=30,
            width=70
        )
        backup_btn.pack(side="left", padx=3)
        
        # RESTORE
        restore_btn = ctk.CTkButton(
            right_frame, 
            text="🔄 RESTORE", 
            command=self.restaurer_backup,
            fg_color=COLORS["dark"],
            hover_color="#2c3e50",
            height=30,
            width=70
        )
        restore_btn.pack(side="left", padx=3)
        
        # DÉCONNEXION
        logout_btn = ctk.CTkButton(
            right_frame, 
            text="🚪 DÉCONNEXION", 
            command=self.nav_manager.logout,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_dark"],
            height=30,
            width=90
        )
        logout_btn.pack(side="left", padx=5)
        
        # Info utilisateur
        role = "Admin" if self.auth_manager.is_admin() else "User"
        user_label = ctk.CTkLabel(
            right_frame, 
            text=f"{self.auth_manager.current_user} ({role})",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["primary"]
        )
        user_label.pack(side="left", padx=5)
    
    def faire_backup(self):
        from database import BibliothequeDB
        db = BibliothequeDB()
        msg = db.backup_database()
        messagebox.showinfo("Backup", msg)
    
    def restaurer_backup(self):
        from database import BibliothequeDB
        db = BibliothequeDB()
        success, message = db.restaurer_backup_interactif()
        if success:
            if hasattr(self.nav_manager, 'current_view') and self.nav_manager.current_view:
                if hasattr(self.nav_manager.current_view, 'rafraichir_liste'):
                    self.nav_manager.current_view.rafraichir_liste()
            messagebox.showinfo("Succès", message)
        else:
            messagebox.showerror("Erreur", message)


class BibliothequeApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("📚 Bibliothèque Intelligente")
        self.root.geometry("1300x800")  # Taille fixe
        
        self.auth_manager = AuthManager()
        self.show_login()
        self.root.mainloop()
    
    def show_login(self):
        from login_dialog import show_login_screen
        show_login_screen(self.root, self.auth_manager)


if __name__ == "__main__":
    app = BibliothequeApp()