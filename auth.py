# auth.py - Système d'authentification

import hashlib
import json
import os
from datetime import datetime

class AuthManager:
    """Gestionnaire d'authentification avec chiffrement"""
    
    def __init__(self):
        self.users_file = "users.json"
        self.current_user = None
        self.load_users()
    
    def load_users(self):
        """Charge les utilisateurs depuis le fichier JSON"""
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        else:
            # Créer un compte admin par défaut
            self.users = {
                "admin": {
                    "password": self.hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
            }
            self.save_users()
    
    def save_users(self):
        """Sauvegarde les utilisateurs"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, indent=4, ensure_ascii=False)
    
    def hash_password(self, password):
        """Hash le mot de passe avec SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password, hashed):
        """Vérifie le mot de passe"""
        return self.hash_password(password) == hashed
    
    def login(self, username, password):
        """Authentifie un utilisateur"""
        if username in self.users:
            if self.verify_password(password, self.users[username]["password"]):
                self.current_user = username
                return True, f"✅ Bienvenue {username} !"
        return False, "❌ Identifiants incorrects"
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        self.current_user = None
        return True, "👋 Déconnecté avec succès"
    
    def add_user(self, username, password, role="user"):
        """Ajoute un nouvel utilisateur (admin uniquement)"""
        if username in self.users:
            return False, "❌ Cet utilisateur existe déjà"
        
        self.users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.save_users()
        return True, f"✅ Utilisateur '{username}' ajouté"
    
    def delete_user(self, username):
        """Supprime un utilisateur (admin uniquement)"""
        if username == "admin":
            return False, "❌ Impossible de supprimer le compte admin"
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True, f"✅ Utilisateur '{username}' supprimé"
        return False, "❌ Utilisateur non trouvé"
    
    def get_users_list(self):
        """Retourne la liste des utilisateurs (sans les mots de passe)"""
        users_list = []
        for username, data in self.users.items():
            users_list.append({
                "username": username,
                "role": data["role"],
                "created_at": data["created_at"]
            })
        return users_list
    
    def is_admin(self):
        """Vérifie si l'utilisateur courant est admin"""
        if self.current_user and self.current_user in self.users:
            return self.users[self.current_user]["role"] == "admin"
        return False
    
    def is_authenticated(self):
        """Vérifie si un utilisateur est connecté"""
        return self.current_user is not None