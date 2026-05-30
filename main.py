# main.py
# Application principale - Interface graphique moderne avec CustomTkinter

import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import threading
from database import BibliothequeDB
from models import Livre
from chatbot import ChatbotBibliotheque

# Configuration du thème moderne
ctk.set_appearance_mode("dark")  # "dark" ou "light"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class BibliothequeApp:
    """
    Application principale de gestion de bibliothèque avec chatbot IA
    Interface moderne, CRUD complet, chatbot intelligent
    """
    
    def __init__(self):
        """Initialise la fenêtre principale et tous les composants"""
        
        # Fenêtre principale
        self.root = ctk.CTk()
        self.root.title("📚 Bibliothèque Intelligente - Gestion de livres avec Chatbot IA")
        self.root.geometry("1400x800")
        
        # Base de données et chatbot
        self.db = BibliothequeDB()
        self.chatbot = None
        self.livre_a_modifier_id = None  # Pour savoir si on modifie un livre
        
        # Initialiser le chatbot dans un thread séparé
        self.init_chatbot_async()
        
        # Créer l'interface
        self.setup_ui()
        
        # Charger les livres
        self.rafraichir_liste()
        
        # Lancer l'application
        self.root.mainloop()
    
    def init_chatbot_async(self):
        """Initialise le chatbot en arrière-plan"""
        def init():
            try:
                self.chatbot = ChatbotBibliotheque()
                self.bouton_chat.configure(state="normal")
                print("🤖 Chatbot prêt !")
            except Exception as e:
                print(f"⚠️ Chatbot non disponible : {e}")
                self.chatbot = None
        
        thread = threading.Thread(target=init)
        thread.start()
    
    def setup_ui(self):
        """Configure toute l'interface utilisateur"""
        
        # Frame principale avec deux colonnes
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=2)
        self.root.grid_rowconfigure(0, weight=1)
        
        # ==================== PARTIE GAUCHE : CRUD ====================
        left_frame = ctk.CTkFrame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Titre CRUD
        title_crud = ctk.CTkLabel(left_frame, text="📖 GESTION DES LIVRES", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_crud.pack(pady=10)
        
        # Frame formulaire
        form_frame = ctk.CTkFrame(left_frame)
        form_frame.pack(fill="x", padx=15, pady=10)
        
        # Champs du formulaire (2 colonnes)
        # Ligne 1 : Titre
        ctk.CTkLabel(form_frame, text="Titre :", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_titre = ctk.CTkEntry(form_frame, width=200, placeholder_text="Titre du livre")
        self.entry_titre.grid(row=0, column=1, padx=5, pady=5)
        
        # Ligne 2 : Auteur
        ctk.CTkLabel(form_frame, text="Auteur :", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_auteur = ctk.CTkEntry(form_frame, width=200, placeholder_text="Nom de l'auteur")
        self.entry_auteur.grid(row=1, column=1, padx=5, pady=5)
        
        # Ligne 3 : Catégorie
        ctk.CTkLabel(form_frame, text="Catégorie :", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_categorie = ctk.CTkEntry(form_frame, width=200, placeholder_text="Roman, Science, Histoire...")
        self.entry_categorie.grid(row=2, column=1, padx=5, pady=5)
        
        # Ligne 4 : Année
        ctk.CTkLabel(form_frame, text="Année :", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.entry_annee = ctk.CTkEntry(form_frame, width=200, placeholder_text="2024")
        self.entry_annee.grid(row=3, column=1, padx=5, pady=5)
        
        # Ligne 5 : Quantité
        ctk.CTkLabel(form_frame, text="Quantité :", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.entry_quantite = ctk.CTkEntry(form_frame, width=200, placeholder_text="1")
        self.entry_quantite.grid(row=4, column=1, padx=5, pady=5)
        
        # Ligne 6 : Statut
        ctk.CTkLabel(form_frame, text="Statut :", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.combo_statut = ctk.CTkComboBox(form_frame, values=["disponible", "emprunté", "réservé"], width=200)
        self.combo_statut.grid(row=5, column=1, padx=5, pady=5)
        
        # Boutons CRUD
        btn_frame = ctk.CTkFrame(left_frame)
        btn_frame.pack(pady=10)
        
        self.btn_ajouter = ctk.CTkButton(btn_frame, text="➕ AJOUTER", command=self.ajouter_livre, 
                                          fg_color="#2ecc71", hover_color="#27ae60", width=120)
        self.btn_ajouter.grid(row=0, column=0, padx=5)
        
        self.btn_modifier = ctk.CTkButton(btn_frame, text="✏️ MODIFIER", command=self.preparer_modification, 
                                           fg_color="#3498db", hover_color="#2980b9", width=120)
        self.btn_modifier.grid(row=0, column=1, padx=5)
        
        self.btn_supprimer = ctk.CTkButton(btn_frame, text="🗑️ SUPPRIMER", command=self.supprimer_livre, 
                                            fg_color="#e74c3c", hover_color="#c0392b", width=120)
        self.btn_supprimer.grid(row=0, column=2, padx=5)
        
        self.btn_annuler = ctk.CTkButton(btn_frame, text="❌ ANNULER", command=self.annuler_modification, 
                                          fg_color="#95a5a6", hover_color="#7f8c8d", width=120)
        self.btn_annuler.grid(row=0, column=3, padx=5)
        self.btn_annuler.configure(state="disabled")
        
        # Frame recherche
        search_frame = ctk.CTkFrame(left_frame)
        search_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(search_frame, text="🔍 Rechercher :", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        self.entry_recherche = ctk.CTkEntry(search_frame, placeholder_text="Titre, auteur ou ID...")
        self.entry_recherche.pack(side="left", fill="x", expand=True, padx=5)
        ctk.CTkButton(search_frame, text="Chercher", command=self.rechercher_livres, width=80).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Tous", command=self.rafraichir_liste, width=80).pack(side="left", padx=5)
        
        # ==================== PARTIE DROITE : CHATBOT ====================
        right_frame = ctk.CTkFrame(self.root)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Titre Chatbot
        title_chat = ctk.CTkLabel(right_frame, text="🤖 CHATBOT INTELLIGENT", 
                                   font=ctk.CTkFont(size=20, weight="bold"))
        title_chat.pack(pady=10)
        
        # Zone d'affichage du chat
        self.chat_display = scrolledtext.ScrolledText(right_frame, wrap="word", font=("Segoe UI", 11), height=25)
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.config(state="disabled", bg="#1e1e1e", fg="#ffffff")
        
        # Afficher message de bienvenue
        self.afficher_message_chat("🤖", "Bonjour ! Je suis votre assistant bibliothécaire. Posez-moi des questions sur les livres !")
        self.afficher_message_chat("🤖", "Exemples :\n• ID 2 existe ?\n• Les Misérables disponible ?\n• Je veux un roman romantique\n• Livres de Victor Hugo")
        
        # Zone de saisie
        input_frame = ctk.CTkFrame(right_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.entry_chat = ctk.CTkEntry(input_frame, placeholder_text="Posez votre question ici...", height=40)
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.bouton_chat = ctk.CTkButton(input_frame, text="ENVOYER", command=self.envoyer_question, 
                                          fg_color="#9b59b6", hover_color="#8e44ad", width=100, height=40)
        self.bouton_chat.pack(side="right")
        self.bouton_chat.configure(state="disabled")  # Désactivé le temps que le chatbot se charge
        
        # Lier la touche Entrée à l'envoi
        self.entry_chat.bind("<Return>", lambda event: self.envoyer_question())
        
        # ==================== LISTE DES LIVRES (au centre) ====================
        # Frame pour la liste
        list_frame = ctk.CTkFrame(self.root)
        list_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.root.grid_columnconfigure(2, weight=3)
        
        ctk.CTkLabel(list_frame, text="📚 CATALOGUE DES LIVRES", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Treeview pour afficher les livres (CustomTkinter n'a pas de tableau, on utilise un ScrolledText formaté)
        self.liste_livres = scrolledtext.ScrolledText(list_frame, wrap="none", font=("Consolas", 10), height=35)
        self.liste_livres.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuration des couleurs
        self.liste_livres.config(bg="#1a1a2e", fg="#e0e0e0", insertbackground="white")
    
    def rafraichir_liste(self):
        """Affiche tous les livres dans la liste"""
        livres = self.db.afficher_tous_les_livres()
        
        self.liste_livres.config(state="normal")
        self.liste_livres.delete("1.0", "end")
        
        # En-tête
        header = f"{'ID':<4} | {'TITRE':<35} | {'AUTEUR':<25} | {'CATÉGORIE':<15} | {'ANNÉE':<6} | {'QTY':<3} | {'STATUT':<12}\n"
        header += "-" * 120 + "\n"
        self.liste_livres.insert("end", header)
        
        for livre in livres:
            ligne = f"{livre.id_livre:<4} | {livre.titre:<35} | {livre.auteur:<25} | {livre.categorie:<15} | {livre.annee_publication:<6} | {livre.quantite_disponible:<3} | {livre.statut:<12}\n"
            self.liste_livres.insert("end", ligne)
        
        self.liste_livres.config(state="disabled")
    
    def rechercher_livres(self):
        """Recherche des livres par titre, auteur ou ID"""
        terme = self.entry_recherche.get().strip()
        if not terme:
            self.rafraichir_liste()
            return
        
        self.liste_livres.config(state="normal")
        self.liste_livres.delete("1.0", "end")
        
        header = f"{'ID':<4} | {'TITRE':<35} | {'AUTEUR':<25} | {'CATÉGORIE':<15} | {'ANNÉE':<6} | {'QTY':<3} | {'STATUT':<12}\n"
        header += "-" * 120 + "\n"
        self.liste_livres.insert("end", header)
        
        # Recherche par ID si numérique
        if terme.isdigit():
            livre = self.db.rechercher_par_id(int(terme))
            if livre:
                ligne = f"{livre.id_livre:<4} | {livre.titre:<35} | {livre.auteur:<25} | {livre.categorie:<15} | {livre.annee_publication:<6} | {livre.quantite_disponible:<3} | {livre.statut:<12}\n"
                self.liste_livres.insert("end", ligne)
        else:
            # Recherche par titre ou auteur
            resultats = self.db.rechercher_par_titre(terme)
            resultats += [l for l in self.db.rechercher_par_auteur(terme) if l not in resultats]
            
            for livre in resultats:
                ligne = f"{livre.id_livre:<4} | {livre.titre:<35} | {livre.auteur:<25} | {livre.categorie:<15} | {livre.annee_publication:<6} | {livre.quantite_disponible:<3} | {livre.statut:<12}\n"
                self.liste_livres.insert("end", ligne)
        
        self.liste_livres.config(state="disabled")
    
    def ajouter_livre(self):
        """Ajoute un nouveau livre"""
        try:
            titre = self.entry_titre.get().strip()
            auteur = self.entry_auteur.get().strip()
            categorie = self.entry_categorie.get().strip()
            annee = int(self.entry_annee.get().strip())
            quantite = int(self.entry_quantite.get().strip())
            statut = self.combo_statut.get()
            
            if not titre or not auteur:
                messagebox.showerror("Erreur", "Le titre et l'auteur sont obligatoires")
                return
            
            livre = Livre(
                titre=titre,
                auteur=auteur,
                categorie=categorie,
                annee_publication=annee,
                quantite_disponible=quantite,
                statut=statut
            )
            
            self.db.ajouter_livre(livre)
            self.rafraichir_liste()
            self.vider_formulaire()
            messagebox.showinfo("Succès", f"Livre '{titre}' ajouté avec succès !")
            
        except ValueError:
            messagebox.showerror("Erreur", "L'année et la quantité doivent être des nombres")
    
    def preparer_modification(self):
        """Prépare la modification d'un livre"""
        selection = self.liste_livres.get("insert linestart", "insert lineend")
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un livre dans la liste")
            return
        
        # Extraire l'ID depuis la ligne sélectionnée
        try:
            id_livre = int(selection.split("|")[0].strip())
            livre = self.db.rechercher_par_id(id_livre)
            
            if livre:
                self.livre_a_modifier_id = livre.id_livre
                self.entry_titre.delete(0, "end")
                self.entry_titre.insert(0, livre.titre)
                self.entry_auteur.delete(0, "end")
                self.entry_auteur.insert(0, livre.auteur)
                self.entry_categorie.delete(0, "end")
                self.entry_categorie.insert(0, livre.categorie)
                self.entry_annee.delete(0, "end")
                self.entry_annee.insert(0, str(livre.annee_publication))
                self.entry_quantite.delete(0, "end")
                self.entry_quantite.insert(0, str(livre.quantite_disponible))
                self.combo_statut.set(livre.statut)
                
                self.btn_ajouter.configure(state="disabled")
                self.btn_modifier.configure(text="💾 VALIDER MODIF", command=self.valider_modification)
                self.btn_annuler.configure(state="normal")
        except:
            pass
    
    def valider_modification(self):
        """Valide la modification d'un livre"""
        if not self.livre_a_modifier_id:
            return
        
        try:
            modifications = {}
            
            titre = self.entry_titre.get().strip()
            if titre:
                modifications['titre'] = titre
            
            auteur = self.entry_auteur.get().strip()
            if auteur:
                modifications['auteur'] = auteur
            
            categorie = self.entry_categorie.get().strip()
            if categorie:
                modifications['categorie'] = categorie
            
            annee = self.entry_annee.get().strip()
            if annee:
                modifications['annee_publication'] = int(annee)
            
            quantite = self.entry_quantite.get().strip()
            if quantite:
                modifications['quantite_disponible'] = int(quantite)
            
            modifications['statut'] = self.combo_statut.get()
            
            self.db.modifier_livre(self.livre_a_modifier_id, **modifications)
            self.rafraichir_liste()
            self.annuler_modification()
            messagebox.showinfo("Succès", "Livre modifié avec succès !")
            
        except ValueError:
            messagebox.showerror("Erreur", "L'année et la quantité doivent être des nombres")
    
    def annuler_modification(self):
        """Annule la modification en cours"""
        self.livre_a_modifier_id = None
        self.vider_formulaire()
        self.btn_ajouter.configure(state="normal")
        self.btn_modifier.configure(text="✏️ MODIFIER", command=self.preparer_modification)
        self.btn_annuler.configure(state="disabled")
    
    def supprimer_livre(self):
        """Supprime un livre"""
        selection = self.liste_livres.get("insert linestart", "insert lineend")
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un livre dans la liste")
            return
        
        try:
            id_livre = int(selection.split("|")[0].strip())
            
            if messagebox.askyesno("Confirmation", f"Supprimer définitivement le livre ID {id_livre} ?"):
                self.db.supprimer_livre(id_livre)
                self.rafraichir_liste()
                messagebox.showinfo("Succès", "Livre supprimé !")
        except:
            pass
    
    def vider_formulaire(self):
        """Vide tous les champs du formulaire"""
        self.entry_titre.delete(0, "end")
        self.entry_auteur.delete(0, "end")
        self.entry_categorie.delete(0, "end")
        self.entry_annee.delete(0, "end")
        self.entry_quantite.delete(0, "end")
        self.combo_statut.set("disponible")
    
    def afficher_message_chat(self, expediteur, message):
        """Affiche un message dans la zone de chat"""
        self.chat_display.config(state="normal")
        
        if expediteur == "🤖":
            self.chat_display.insert("end", f"\n{expediteur} :\n", "bot")
            self.chat_display.insert("end", f"  {message}\n", "bot_msg")
            self.chat_display.tag_config("bot", foreground="#9b59b6", font=("Segoe UI", 11, "bold"))
            self.chat_display.tag_config("bot_msg", foreground="#bbbbbb")
        else:
            self.chat_display.insert("end", f"\n👤 MOI :\n", "user")
            self.chat_display.insert("end", f"  {message}\n", "user_msg")
            self.chat_display.tag_config("user", foreground="#3498db", font=("Segoe UI", 11, "bold"))
            self.chat_display.tag_config("user_msg", foreground="#ffffff")
        
        self.chat_display.see("end")
        self.chat_display.config(state="disabled")
    
    def envoyer_question(self):
        """Envoie une question au chatbot"""
        question = self.entry_chat.get().strip()
        if not question:
            return
        
        # Afficher la question
        self.afficher_message_chat("👤", question)
        self.entry_chat.delete(0, "end")
        
        # Désactiver le bouton pendant la réponse
        self.bouton_chat.configure(state="disabled", text="Génération...")
        
        # Répondre dans un thread séparé
        def repondre():
            try:
                if self.chatbot:
                    reponse = self.chatbot.poser_question(question)
                else:
                    reponse = "⚠️ Chatbot non disponible. Vérifie ta connexion ou ta clé API."
                
                self.root.after(0, lambda: self.afficher_message_chat("🤖", reponse))
            except Exception as e:
                self.root.after(0, lambda: self.afficher_message_chat("🤖", f"❌ Erreur : {str(e)}"))
            finally:
                self.root.after(0, lambda: self.bouton_chat.configure(state="normal", text="ENVOYER"))
        
        thread = threading.Thread(target=repondre)
        thread.start()


# ==================== LANCEMENT DE L'APPLICATION ====================

if __name__ == "__main__":
    print("🚀 Lancement de l'application Bibliothèque Intelligente...")
    print("="*60)
    app = BibliothequeApp()