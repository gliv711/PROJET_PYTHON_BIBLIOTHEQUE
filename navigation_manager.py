# navigation_manager.py - Gestionnaire de navigation SPA

import customtkinter as ctk
from tkinter import messagebox
from styles import COLORS

class NavigationManager:
    """Gère la navigation entre les différentes vues de l'application"""
    
    def __init__(self, parent, auth_manager):
        self.parent = parent
        self.auth_manager = auth_manager
        self.history = []
        self.current_view = None
        self.view_container = None
        
        self.setup_container()
    
    def setup_container(self):
        """Configure le conteneur principal pour les vues"""
        self.view_container = ctk.CTkFrame(self.parent, fg_color=COLORS["darker"])
        self.view_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    def navigate_to(self, view_class, **kwargs):
        """Navigue vers une nouvelle vue"""
        
        # Sauvegarder dans l'historique
        if self.current_view:
            self.history.append(self.current_view)
        
        # Supprimer l'ancienne vue
        if self.current_view:
            self.current_view.destroy()
        
        # Créer la nouvelle vue
        self.current_view = view_class(
            self.view_container, 
            self, 
            **kwargs
        )
        self.current_view.pack(fill="both", expand=True)
    
    def go_back(self):
        """Retourne à la vue précédente"""
        if self.history:
            previous_view = self.history.pop()
            if self.current_view:
                self.current_view.destroy()
            self.current_view = previous_view
            self.current_view.pack(fill="both", expand=True)
        else:
            messagebox.showinfo("Navigation", "Vous êtes déjà sur l'écran d'accueil")
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        if messagebox.askyesno("Déconnexion", "Voulez-vous vraiment vous déconnecter ?"):
            self.auth_manager.logout()
            # Nettoyer et revenir à l'écran de connexion
            for widget in self.parent.winfo_children():
                widget.destroy()
            
            # Recréer l'écran de connexion
            from login_dialog import show_login_screen
            show_login_screen(self.parent, self.auth_manager)
    
    def clear_history(self):
        """Vide l'historique"""
        self.history = []