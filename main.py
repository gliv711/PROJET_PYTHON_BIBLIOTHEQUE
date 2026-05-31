# main.py - Version avec Treeview pour un tableau stable et moderne

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re
import random
from datetime import datetime
from database import BibliothequeDB
from models import Livre
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ==================== POPUP AJOUT/MODIFICATION ====================

class AjouterLivreDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("📖 Ajouter un nouveau livre")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        self.setup_ui()
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text="➕ NOUVEAU LIVRE", font=ctk.CTkFont(size=22, weight="bold"))
        title.pack(pady=20)
        
        form = ctk.CTkFrame(self)
        form.pack(padx=30, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(form, text="Titre *", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_titre = ctk.CTkEntry(form, width=300, placeholder_text="Titre du livre")
        self.entry_titre.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Auteur *", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_auteur = ctk.CTkEntry(form, width=300, placeholder_text="Nom de l'auteur")
        self.entry_auteur.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Catégorie", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.combo_categorie = ctk.CTkComboBox(form, values=["Roman", "Science", "Histoire", "Informatique", "Polar", "Fantasy", "Autre"], width=300)
        self.combo_categorie.set("Roman")
        self.combo_categorie.grid(row=2, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Année", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_annee = ctk.CTkEntry(form, width=300, placeholder_text="2024")
        self.entry_annee.grid(row=3, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Quantité", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.entry_quantite = ctk.CTkEntry(form, width=300, placeholder_text="1")
        self.entry_quantite.grid(row=4, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Statut", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.combo_statut = ctk.CTkComboBox(form, values=["disponible", "emprunté", "réservé"], width=300)
        self.combo_statut.set("disponible")
        self.combo_statut.grid(row=5, column=1, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="✓ AJOUTER", command=self.ajouter, fg_color="#2ecc71", hover_color="#27ae60", width=120, height=40).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="✗ ANNULER", command=self.destroy, fg_color="#e74c3c", hover_color="#c0392b", width=120, height=40).pack(side="left", padx=10)
    
    def ajouter(self):
        titre = self.entry_titre.get().strip()
        auteur = self.entry_auteur.get().strip()
        if not titre or not auteur:
            messagebox.showerror("Erreur", "Le titre et l'auteur sont obligatoires")
            return
        try:
            annee = int(self.entry_annee.get()) if self.entry_annee.get() else 2000
            quantite = int(self.entry_quantite.get()) if self.entry_quantite.get() else 1
        except ValueError:
            messagebox.showerror("Erreur", "L'année et la quantité doivent être des nombres")
            return
        livre = Livre(titre=titre, auteur=auteur, categorie=self.combo_categorie.get(),
                     annee_publication=annee, quantite_disponible=quantite, statut=self.combo_statut.get())
        self.callback(livre)
        self.destroy()


class ModifierLivreDialog(ctk.CTkToplevel):
    def __init__(self, parent, livre, callback):
        super().__init__(parent)
        self.livre = livre
        self.callback = callback
        self.title(f"✏️ Modifier - {livre.titre}")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        self.setup_ui()
    
    def setup_ui(self):
        title = ctk.CTkLabel(self, text=f"✏️ MODIFIER - ID {self.livre.id_livre}", font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        form = ctk.CTkFrame(self)
        form.pack(padx=30, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(form, text="Titre", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_titre = ctk.CTkEntry(form, width=300)
        self.entry_titre.insert(0, self.livre.titre)
        self.entry_titre.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Auteur", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_auteur = ctk.CTkEntry(form, width=300)
        self.entry_auteur.insert(0, self.livre.auteur)
        self.entry_auteur.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Catégorie", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.combo_categorie = ctk.CTkComboBox(form, values=["Roman", "Science", "Histoire", "Informatique", "Polar", "Fantasy", "Autre"], width=300)
        self.combo_categorie.set(self.livre.categorie)
        self.combo_categorie.grid(row=2, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Année", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.entry_annee = ctk.CTkEntry(form, width=300)
        self.entry_annee.insert(0, str(self.livre.annee_publication))
        self.entry_annee.grid(row=3, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Quantité", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.entry_quantite = ctk.CTkEntry(form, width=300)
        self.entry_quantite.insert(0, str(self.livre.quantite_disponible))
        self.entry_quantite.grid(row=4, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Statut", font=ctk.CTkFont(weight="bold")).grid(row=5, column=0, padx=10, pady=10, sticky="w")
        self.combo_statut = ctk.CTkComboBox(form, values=["disponible", "emprunté", "réservé"], width=300)
        self.combo_statut.set(self.livre.statut)
        self.combo_statut.grid(row=5, column=1, padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 VALIDER", command=self.valider, fg_color="#3498db", hover_color="#2980b9", width=120, height=40).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="✗ ANNULER", command=self.destroy, fg_color="#95a5a6", hover_color="#7f8c8d", width=120, height=40).pack(side="left", padx=10)
    
    def valider(self):
        modifications = {}
        titre = self.entry_titre.get().strip()
        if titre and titre != self.livre.titre:
            modifications['titre'] = titre
        auteur = self.entry_auteur.get().strip()
        if auteur and auteur != self.livre.auteur:
            modifications['auteur'] = auteur
        categorie = self.combo_categorie.get()
        if categorie != self.livre.categorie:
            modifications['categorie'] = categorie
        try:
            annee = int(self.entry_annee.get())
            if annee != self.livre.annee_publication:
                modifications['annee_publication'] = annee
        except:
            pass
        try:
            quantite = int(self.entry_quantite.get())
            if quantite != self.livre.quantite_disponible:
                modifications['quantite_disponible'] = quantite
        except:
            pass
        statut = self.combo_statut.get()
        if statut != self.livre.statut:
            modifications['statut'] = statut
        if modifications:
            self.callback(self.livre.id_livre, modifications)
        self.destroy()


# ==================== CHATBOT GEMINI - 100% IA ====================

import google.generativeai as genai
from config import get_api_key

class ChatbotIntelligent:
    def __init__(self, db):
        self.db = db
        self.historique = []
        self.gemini_available = False
        
        try:
            api_key = get_api_key()
            if not api_key:
                print("❌ Clé API non trouvée dans .env")
                return
            
            genai.configure(api_key=api_key)
            
            # Lister les modèles disponibles
            print("🔍 Recherche des modèles disponibles...")
            modeles_disponibles = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    modeles_disponibles.append(m.name)
                    print(f"  - {m.name}")
            
            # Choisir le meilleur modèle disponible
            modele_choisi = None
            for m in ['models/gemini-1.0-pro', 'models/gemini-pro', 'gemini-1.0-pro']:
                if m in modeles_disponibles or m.replace('models/', '') in modeles_disponibles:
                    modele_choisi = m
                    break
            
            if not modele_choisi and modeles_disponibles:
                modele_choisi = modeles_disponibles[0]
            
            if modele_choisi:
                self.model = genai.GenerativeModel(modele_choisi)
                print(f"✅ Gemini activé avec: {modele_choisi}")
                self.gemini_available = True
            else:
                print("❌ Aucun modèle Gemini trouvé")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")
    
    def get_contexte(self):
        """Retourne tous les livres formatés"""
        livres = self.db.afficher_tous_les_livres()
        if not livres:
            return "Aucun livre dans la bibliothèque."
        
        texte = "📚 BIBLIOTHÈQUE:\n"
        for livre in livres:
            texte += f"• ID:{livre.id_livre} | {livre.titre} | {livre.auteur} | {livre.categorie} | {livre.statut}\n"
        return texte
    
    def get_reponse(self, message):
        """100% Gemini"""
        
        if not self.gemini_available:
            return self.get_reponse_secours(message)
        
        self.historique.append(f"User: {message}")
        if len(self.historique) > 10:
            self.historique = self.historique[-10:]
        
        contexte = self.get_contexte()
        
        prompt = f"""Tu es un assistant de bibliothèque amical. Voici tous les livres :

{contexte}

Règles :
- Réponds UNIQUEMENT avec les livres listés
- Utilise des émojis
- Réponds en français, naturellement

Question : {message}

Réponse :"""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Erreur: {e}")
            return self.get_reponse_secours(message)
    
    def get_reponse_secours(self, message):
        """Mode secours basé sur la base de données"""
        message_lower = message.lower()
        livres = self.db.afficher_tous_les_livres()
        
        # Livres disponibles
        if "disponible" in message_lower:
            dispo = [l for l in livres if l.statut == "disponible"]
            if dispo:
                reponse = "📚 **Livres disponibles :**\n\n"
                for l in dispo[:15]:
                    reponse += f"✅ *{l.titre}* – {l.auteur}\n"
                return reponse
        
        # Recherche par ID
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            for num in numbers:
                livre = self.db.rechercher_par_id(int(num))
                if livre:
                    return f"✅ ID {num}: {livre.titre} par {livre.auteur} - {livre.statut}"
        
        # Recherche par auteur
        for livre in livres:
            if livre.auteur.lower() in message_lower:
                return f"📚 Livres de {livre.auteur} : " + ", ".join([l.titre for l in self.db.rechercher_par_auteur(livre.auteur)])
        
        # Recherche par titre
        for livre in livres:
            if livre.titre.lower() in message_lower:
                return f"📖 {livre.titre} - {livre.auteur} ({livre.statut})"
        
        return "🤖 Je n'ai pas compris. Tapez 'livres disponibles' pour voir le catalogue."
class DashboardStatistiques(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("📊 Dashboard - Statistiques")
        self.geometry("900x700")
        self.transient(parent)
        
        self.setup_ui()
        self.creer_graphiques()
    
    def setup_ui(self):
        btn_export = ctk.CTkButton(self, text="📁 EXPORT CSV", command=self.exporter_csv,
                                   fg_color="#2ecc71", hover_color="#27ae60")
        btn_export.pack(pady=10)
        
        self.frame_graph = ctk.CTkFrame(self)
        self.frame_graph.pack(fill="both", expand=True, padx=10, pady=10)
    
    def creer_graphiques(self):
        stats = self.db.get_statistiques()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.patch.set_facecolor('#1e1e2e')
        
        statuts = ['disponibles', 'empruntés', 'réservés']
        valeurs = [stats['disponibles'], stats['empruntes'], stats['reserves']]
        couleurs = ['#2ecc71', '#e74c3c', '#f39c12']
        ax1.pie(valeurs, labels=statuts, colors=couleurs, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Répartition par statut', color='white')
        ax1.set_facecolor('#1e1e2e')
        
        categories = list(stats['categories'].items())[:5]
        noms = [c[0][:12] for c in categories]
        counts = [c[1] for c in categories]
        bars = ax2.bar(noms, counts, color='#9b59b6')
        ax2.set_title('Top 5 catégories', color='white')
        ax2.set_xlabel('Catégories', color='white')
        ax2.set_ylabel('Nombre de livres', color='white')
        ax2.tick_params(colors='white')
        ax2.set_facecolor('#1e1e2e')
        for bar, val in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, str(val), ha='center', color='white')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        info_text = f"""
📊 STATISTIQUES GÉNÉRALES:
• Total livres: {stats['total']}
• Année moyenne: {stats['annee_moyenne']}
• Plus ancien: {stats['plus_ancien'].titre if stats['plus_ancien'] else 'N/A'}
• Plus récent: {stats['plus_recent'].titre if stats['plus_recent'] else 'N/A'}
        """
        label_info = ctk.CTkLabel(self, text=info_text, font=ctk.CTkFont(size=12), justify="left")
        label_info.pack(pady=10)
    
    def exporter_csv(self):
        message = self.db.exporter_csv("dashboard_export.csv")
        messagebox.showinfo("Export", f"Données exportées vers dashboard_export.csv")


# ==================== APPLICATION PRINCIPALE ====================

class BibliothequeApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("📚 Bibliothèque Intelligente")
        self.root.geometry("1300x750")
        
        self.db = BibliothequeDB()
        self.chatbot = ChatbotIntelligent(self.db)
        
        self.setup_ui()
        self.rafraichir_liste()
        
        self.root.mainloop()
    
    def setup_ui(self):
        toolbar = ctk.CTkFrame(self.root, height=50, fg_color="#1a1a2e")
        toolbar.pack(fill="x", padx=10, pady=(10, 5))
        toolbar.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        title_frame.pack(side="left", padx=20)
        ctk.CTkLabel(title_frame, text="📚", font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(title_frame, text="BIBLIOTHÈQUE INTELLIGENTE", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=10)
        
        self.stats_label = ctk.CTkLabel(toolbar, text="📊 0 livres", font=ctk.CTkFont(size=12), text_color="#888")
        self.stats_label.pack(side="left", padx=10)
        
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(btn_frame, text="➕ AJOUTER", command=self.ouvrir_ajout, fg_color="#2ecc71", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✏️ MODIFIER", command=self.ouvrir_modification, fg_color="#3498db", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🗑️ SUPPRIMER", command=self.supprimer_livre, fg_color="#e74c3c", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📤 EMPRUNTER", command=self.ouvrir_emprunt, fg_color="#f39c12", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📥 RETOUR", command=self.ouvrir_retour, fg_color="#1abc9c", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📊 DASHBOARD", command=self.ouvrir_dashboard, fg_color="#9b59b6", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="💾 BACKUP", command=self.faire_backup, fg_color="#2c3e50", height=35, width=70).pack(side="left", padx=2)
        
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        self.entry_recherche = ctk.CTkEntry(search_frame, placeholder_text="🔍 Rechercher...", width=250)
        self.entry_recherche.pack(side="left", padx=5)
        self.entry_recherche.bind("<Return>", lambda e: self.rechercher())
        ctk.CTkButton(search_frame, text="Chercher", command=self.rechercher, width=60).pack(side="left", padx=2)
        ctk.CTkButton(search_frame, text="Tous", command=self.rafraichir_liste, width=50).pack(side="left", padx=2)
        
        filter_menu = ctk.CTkOptionMenu(search_frame, values=["Filtrer...", "Par catégorie", "Emprunts", "Retards"],
                                        command=self.gestion_filtres, width=100)
        filter_menu.pack(side="left", padx=5)
        
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_catalogue = self.tabview.add("📚 CATALOGUE")
        tab_chatbot = self.tabview.add("🤖 CHATBOT")
        
        # ==================== TABLEAU AVEC TREEVIEW ====================
        # Frame pour le tableau avec Treeview
        tree_frame = ctk.CTkFrame(tab_catalogue, fg_color="#0f0f1a")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Création du Treeview
        self.tree = ttk.Treeview(tree_frame, style="Custom.Treeview", selectmode="extended")
        
        # Style pour le Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview", 
                       background="#1e1e2e",
                       foreground="#ecf0f1",
                       fieldbackground="#1e1e2e",
                       borderwidth=0,
                       rowheight=35)
        style.configure("Custom.Treeview.Heading",
                       background="#1a1a2e",
                       foreground="white",
                       font=("Segoe UI", 11, "bold"),
                       borderwidth=0)
        style.map("Custom.Treeview", background=[('selected', '#3498db')])
        
        # Configuration des colonnes
        columns = ("ID", "TITRE", "AUTEUR", "CATÉGORIE", "ANNÉE", "QTY", "STATUT")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        # Définition des colonnes
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("TITRE", width=380, anchor="w")
        self.tree.column("AUTEUR", width=200, anchor="w")
        self.tree.column("CATÉGORIE", width=130, anchor="w")
        self.tree.column("ANNÉE", width=70, anchor="center")
        self.tree.column("QTY", width=60, anchor="center")
        self.tree.column("STATUT", width=110, anchor="center")
        
        # En-têtes
        self.tree.heading("ID", text="ID", command=lambda: self.trier_par_colonne("ID"))
        self.tree.heading("TITRE", text="TITRE", command=lambda: self.trier_par_colonne("TITRE"))
        self.tree.heading("AUTEUR", text="AUTEUR", command=lambda: self.trier_par_colonne("AUTEUR"))
        self.tree.heading("CATÉGORIE", text="CATÉGORIE", command=lambda: self.trier_par_colonne("CATÉGORIE"))
        self.tree.heading("ANNÉE", text="ANNÉE", command=lambda: self.trier_par_colonne("ANNÉE"))
        self.tree.heading("QTY", text="QTY", command=lambda: self.trier_par_colonne("QTY"))
        self.tree.heading("STATUT", text="STATUT", command=lambda: self.trier_par_colonne("STATUT"))
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        # Bind pour la sélection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Info sélection
        info_frame = ctk.CTkFrame(tab_catalogue, fg_color="transparent", height=30)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.info_label = ctk.CTkLabel(info_frame, text="💡 Cliquez sur un livre pour le sélectionner", 
                                       text_color="#666666", font=ctk.CTkFont(size=10))
        self.info_label.pack()
        
        # ==================== CHATBOT ====================
        chat_container = ctk.CTkFrame(tab_chatbot, fg_color="#1e1e2e")
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(chat_container, wrap="word", font=("Segoe UI", 11),
                                                       bg="#1e1e2e", fg="#ffffff", relief="flat")
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.tag_config("bot", foreground="#9b59b6")
        self.chat_display.tag_config("user", foreground="#3498db")
        
        input_frame = ctk.CTkFrame(tab_chatbot, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_chat = ctk.CTkEntry(input_frame, placeholder_text="💬 Posez votre question...", height=45)
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_chat.bind("<Return>", lambda e: self.envoyer_message())
        self.btn_envoyer = ctk.CTkButton(input_frame, text="ENVOYER", command=self.envoyer_message, fg_color="#9b59b6", height=45)
        self.btn_envoyer.pack(side="right")
        
        self.afficher_message_bienvenue()
    
    def trier_par_colonne(self, col):
        """Trie le tableau par colonne"""
        livres = self.db.afficher_tous_les_livres()
        
        if col == "ID":
            livres.sort(key=lambda x: x.id_livre)
        elif col == "TITRE":
            livres.sort(key=lambda x: x.titre.lower())
        elif col == "AUTEUR":
            livres.sort(key=lambda x: x.auteur.lower())
        elif col == "CATÉGORIE":
            livres.sort(key=lambda x: x.categorie.lower())
        elif col == "ANNÉE":
            livres.sort(key=lambda x: x.annee_publication)
        elif col == "QTY":
            livres.sort(key=lambda x: x.quantite_disponible)
        elif col == "STATUT":
            livres.sort(key=lambda x: x.statut)
        
        self.afficher_livres_dans_tree(livres)
    
    def afficher_livres_dans_tree(self, livres):
        """Affiche la liste des livres dans le Treeview"""
        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Remplir le tableau
        for livre in livres:
            # Couleur du statut
            statut_color = ""
            if livre.statut == "disponible":
                statut_text = f"✅ {livre.statut.upper()}"
            elif livre.statut == "emprunté":
                statut_text = f"📤 {livre.statut.upper()}"
            else:
                statut_text = f"🔒 {livre.statut.upper()}"
            
            self.tree.insert("", "end", iid=str(livre.id_livre), values=(
                livre.id_livre,
                livre.titre[:50],
                livre.auteur[:25],
                livre.categorie[:15],
                livre.annee_publication,
                livre.quantite_disponible,
                statut_text
            ))
        
        # Mettre à jour les couleurs des lignes
        self.update_row_colors()
        
        # Statistiques
        total = len(livres)
        dispo = len([l for l in livres if l.statut == "disponible"])
        self.stats_label.configure(text=f"📊 {total} livres • ✅ {dispo} dispo")
    
    def update_row_colors(self):
        """Met à jour les couleurs des lignes (alternance)"""
        for i, item in enumerate(self.tree.get_children()):
            bg_color = "#2a2a3e" if i % 2 == 0 else "#1e1e2e"
            self.tree.tag_configure(f"row_{i}", background=bg_color)
            self.tree.item(item, tags=(f"row_{i}",))
    
    def on_tree_select(self, event):
        """Gère la sélection dans le Treeview"""
        selected = self.tree.selection()
        if selected:
            self.livre_selectionne = selected[0]
            livre = self.db.rechercher_par_id(int(selected[0]))
            if livre:
                self.info_label.configure(text=f"✅ Livre sélectionné : ID {livre.id_livre} - {livre.titre}",
                                         text_color="#2ecc71")
        else:
            self.livre_selectionne = None
            self.info_label.configure(text="💡 Cliquez sur un livre pour le sélectionner", text_color="#666666")
    
    def rafraichir_liste(self):
        """Rafraîchit l'affichage"""
        livres = self.db.afficher_tous_les_livres()
        self.afficher_livres_dans_tree(livres)
    
    def selectionner_livre(self, row_frame, event=None):
        """Sélectionne un livre (pour compatibilité)"""
        pass
    
    def supprimer_livre(self):
        """Supprime le livre sélectionné"""
        if not hasattr(self, 'livre_selectionne') or not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre à supprimer")
            return
        
        livre = self.db.rechercher_par_id(int(self.livre_selectionne))
        if messagebox.askyesno("Confirmation", f"Supprimer le livre '{livre.titre}' ?"):
            self.db.supprimer_livre(livre.id_livre)
            self.rafraichir_liste()
            self.livre_selectionne = None
            messagebox.showinfo("Succès", "Livre supprimé !")
    
    def supprimer_livres(self):
        self.supprimer_livre()
    
    def ouvrir_ajout(self):
        AjouterLivreDialog(self.root, self.apres_ajout)
    
    def apres_ajout(self, livre):
        self.db.ajouter_livre(livre)
        self.rafraichir_liste()
        messagebox.showinfo("Succès", f"Livre '{livre.titre}' ajouté !")
    
    def ouvrir_modification(self):
        if not hasattr(self, 'livre_selectionne') or not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre à modifier")
            return
        
        livre = self.db.rechercher_par_id(int(self.livre_selectionne))
        ModifierLivreDialog(self.root, livre, self.apres_modification)
    
    def apres_modification(self, id_livre, modifications):
        self.db.modifier_livre(id_livre, **modifications)
        self.rafraichir_liste()
        self.livre_selectionne = None
        messagebox.showinfo("Succès", "Livre modifié !")
    
    def ouvrir_emprunt(self):
        if not hasattr(self, 'livre_selectionne') or not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre à emprunter")
            return
        
        livre = self.db.rechercher_par_id(int(self.livre_selectionne))
        
        if livre.statut == "réservé":
            messagebox.showwarning(
                "Impossible", 
                f"📕 Le livre '{livre.titre}' est **RÉSERVÉ**.\n\n"
                f"Un livre réservé ne peut pas être emprunté.\n\n"
                f"💡 Pour l'emprunter, modifiez d'abord son statut en 'disponible'."
            )
            return
        elif livre.statut != "disponible":
            messagebox.showwarning(
                "Impossible", 
                f"📕 Le livre '{livre.titre}' n'est pas disponible.\n\n"
                f"Statut actuel : {livre.statut.upper()}"
            )
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("📤 Emprunter un livre")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 400) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 300) // 2
        dialog.geometry(f"+{x}+{y}")
        
        ctk.CTkLabel(dialog, text=f"Emprunter : {livre.titre}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        
        ctk.CTkLabel(dialog, text="Nom de l'emprunteur :").pack()
        entry_nom = ctk.CTkEntry(dialog, width=250, placeholder_text="Votre nom")
        entry_nom.pack(pady=5)
        
        ctk.CTkLabel(dialog, text="Durée d'emprunt (jours) :").pack()
        combo_duree = ctk.CTkComboBox(dialog, values=["7", "14", "21", "30"], width=100)
        combo_duree.set("14")
        combo_duree.pack(pady=5)
        
        def valider_emprunt():
            nom = entry_nom.get().strip() or "Anonyme"
            duree = int(combo_duree.get())
            success, message = self.db.emprunter_livre(livre.id_livre, nom, duree)
            messagebox.showinfo("Emprunt", message)
            if success:
                self.rafraichir_liste()
                self.livre_selectionne = None
            dialog.destroy()
        
        ctk.CTkButton(dialog, text="✓ CONFIRMER EMPRUNT", command=valider_emprunt, fg_color="#2ecc71", hover_color="#27ae60", width=200, height=40).pack(pady=20)
    
    def ouvrir_retour(self):
        if not hasattr(self, 'livre_selectionne') or not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre à retourner")
            return
        
        livre = self.db.rechercher_par_id(int(self.livre_selectionne))
        
        if livre.statut == "réservé":
            messagebox.showwarning(
                "Impossible", 
                f"📕 Le livre '{livre.titre}' est **RÉSERVÉ**.\n\n"
                f"Un livre réservé ne peut pas être retourné car il n'est pas emprunté."
            )
            return
        elif livre.statut != "emprunté":
            messagebox.showwarning(
                "Impossible", 
                f"📕 Le livre '{livre.titre}' n'est pas emprunté.\n\n"
                f"Statut actuel : {livre.statut.upper()}"
            )
            return
        
        if messagebox.askyesno("Confirmation", f"Confirmer le retour de '{livre.titre}' ?"):
            success, message = self.db.retourner_livre(livre.id_livre)
            messagebox.showinfo("Retour", message)
            if success:
                self.rafraichir_liste()
                self.livre_selectionne = None
    
    def afficher_message_bienvenue(self):
        self.chat_display.insert("end", "🤖 Bienvenue ! Posez-moi des questions sur les livres.\n", "bot")
    
    def envoyer_message(self):
        message = self.entry_chat.get().strip()
        if not message:
            return
        self.chat_display.insert("end", f"\n👤 {message}\n", "user")
        self.entry_chat.delete(0, "end")
        self.root.update()
        reponse = self.chatbot.get_reponse(message)
        self.chat_display.insert("end", f"🤖 {reponse}\n", "bot")
        self.chat_display.see("end")
    
    def gestion_filtres(self, choix):
        if choix == "Par catégorie":
            self.filtrer_par_categorie()
        elif choix == "Emprunts":
            self.afficher_emprunts()
        elif choix == "Retards":
            self.afficher_retards()
    
    def ouvrir_dashboard(self):
        DashboardStatistiques(self.root, self.db)
    
    def afficher_emprunts(self):
        emprunts = self.db.lister_emprunts_en_cours()
        if not emprunts:
            messagebox.showinfo("Emprunts", "Aucun emprunt en cours")
            return
        texte = "📤 **LISTE DES EMPRUNTS EN COURS**\n\n"
        for e in emprunts:
            texte += f"ID {e['id']} : {e['titre']}\n   👤 {e['emprunteur']}\n   📅 Retour : {e['date_retour']}\n\n"
        messagebox.showinfo("Emprunts en cours", texte)
    
    def afficher_retards(self):
        retards = self.db.verifier_retards()
        if not retards:
            messagebox.showinfo("Retards", "Aucun livre en retard !")
            return
        texte = "⚠️ **LIVRES EN RETARD** ⚠️\n\n"
        for r in retards:
            texte += f"ID {r['id']} : {r['titre']}\n   👤 {r['emprunteur']}\n   ⏰ Retard depuis le {r['date_retour']}\n\n"
        messagebox.showwarning("Livres en retard", texte)
    
    def faire_backup(self):
        message = self.db.backup_database()
        messagebox.showinfo("Sauvegarde", message)
    
    def filtrer_par_categorie(self):
        categories = self.db.get_toutes_categories()
        if not categories:
            messagebox.showinfo("Info", "Aucune catégorie disponible")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Filtrer par catégorie")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Choisissez une catégorie :", font=ctk.CTkFont(weight="bold")).pack(pady=20)
        combo = ctk.CTkComboBox(dialog, values=categories, width=250)
        combo.pack(pady=10)
        
        def appliquer_filtre():
            categorie = combo.get()
            livres_filtres = self.db.filtrer_par_categorie(categorie)
            if livres_filtres:
                self.afficher_livres_dans_tree(livres_filtres)
            else:
                messagebox.showinfo("Résultats", f"Aucun livre dans la catégorie '{categorie}'")
            dialog.destroy()
        
        ctk.CTkButton(dialog, text="APPLIQUER", command=appliquer_filtre, fg_color="#3498db").pack(pady=20)
    
    def rechercher(self):
        terme = self.entry_recherche.get().strip()
        if not terme:
            self.rafraichir_liste()
            return
        
        resultats = []
        if terme.isdigit():
            livre = self.db.rechercher_par_id(int(terme))
            if livre:
                resultats.append(livre)
        else:
            resultats = self.db.rechercher_par_titre(terme)
            for l in self.db.rechercher_par_auteur(terme):
                if l not in resultats:
                    resultats.append(l)
        
        if resultats:
            self.afficher_livres_dans_tree(resultats)
        else:
            self.afficher_livres_dans_tree([])
            messagebox.showinfo("Résultats", f"Aucun résultat pour '{terme}'")


if __name__ == "__main__":
    print("="*60)
    print("📚 BIBLIOTHÈQUE INTELLIGENTE - PROJET SEMESTRIEL")
    print("="*60)
    print("🚀 Lancement de l'application...")
    app = BibliothequeApp()