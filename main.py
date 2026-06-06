# main.py - Version finale corrigée

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import re
from datetime import datetime
from database import BibliothequeDB
from models import Livre
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from chatbot import ChatbotIntelligent  # Import depuis chatbot.py
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

matplotlib.use('TkAgg')

# Configuration du thème
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ==================== POPUPS AJOUT/MODIFICATION ====================

class AjouterLivreDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("📖 Ajouter un livre")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        self.setup_ui()
    
    def setup_ui(self):
        ctk.CTkLabel(self, text="➕ NOUVEAU LIVRE", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        
        form = ctk.CTkFrame(self)
        form.pack(padx=30, pady=10, fill="both", expand=True)
        
        ctk.CTkLabel(form, text="Titre *", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_titre = ctk.CTkEntry(form, width=300)
        self.entry_titre.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Auteur *", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_auteur = ctk.CTkEntry(form, width=300)
        self.entry_auteur.grid(row=1, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(form, text="Catégorie", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.combo_categorie = ctk.CTkComboBox(form, values=["Roman", "Science", "Histoire", "Informatique", "Polar", "Fantasy"], width=300)
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
        ctk.CTkButton(btn_frame, text="✓ AJOUTER", command=self.ajouter, fg_color="#2ecc71", width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="✗ ANNULER", command=self.destroy, fg_color="#e74c3c", width=120).pack(side="left", padx=10)
    
    def ajouter(self):
        titre = self.entry_titre.get().strip()
        auteur = self.entry_auteur.get().strip()
        if not titre or not auteur:
            messagebox.showerror("Erreur", "Titre et auteur requis")
            return
        try:
            annee = int(self.entry_annee.get()) if self.entry_annee.get() else 2000
            quantite = int(self.entry_quantite.get()) if self.entry_quantite.get() else 1
        except ValueError:
            messagebox.showerror("Erreur", "Année et quantité doivent être des nombres")
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
        
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        self.setup_ui()
    
    def setup_ui(self):
        ctk.CTkLabel(self, text=f"✏️ MODIFIER - ID {self.livre.id_livre}", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
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
        self.combo_categorie = ctk.CTkComboBox(form, values=["Roman", "Science", "Histoire", "Informatique", "Polar", "Fantasy"], width=300)
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
        ctk.CTkButton(btn_frame, text="💾 VALIDER", command=self.valider, fg_color="#3498db", width=120).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="✗ ANNULER", command=self.destroy, fg_color="#95a5a6", width=120).pack(side="left", padx=10)
    
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


# ==================== DASHBOARD AMÉLIORÉ ====================

class DashboardStatistiques(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("📊 Dashboard - Statistiques et Emprunts")
        self.geometry("1000x750")
        self.transient(parent)
        
        # Style
        self.configure(fg_color="#0f0f1a")
        
        self.setup_ui()
        self.creer_graphiques()
        self.afficher_emprunteurs()
    
    def setup_ui(self):
        """Interface du dashboard"""
        
        # En-tête
        header = ctk.CTkFrame(self, height=50, fg_color="#1a1a2e")
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header, text="📊 DASHBOARD", font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=20)
        
        # Bouton rafraîchir
        btn_refresh = ctk.CTkButton(header, text="🔄 RAFRAÎCHIR", command=self.rafraichir,
                                   fg_color="#3498db", hover_color="#2980b9", width=120)
        btn_refresh.pack(side="right", padx=10)
        
        # Bouton export
        btn_export = ctk.CTkButton(header, text="📁 EXPORT CSV", command=self.exporter_csv,
                                   fg_color="#2ecc71", hover_color="#27ae60", width=120)
        btn_export.pack(side="right", padx=10)
        
        # Conteneur principal avec deux colonnes
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        main_container.grid_columnconfigure(0, weight=2)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Colonne gauche : Graphiques
        left_frame = ctk.CTkFrame(main_container, fg_color="#1e1e2e", corner_radius=15)
        left_frame.grid(row=0, column=0, padx=(0, 5), sticky="nsew")
        
        ctk.CTkLabel(left_frame, text="📈 STATISTIQUES GRAPHIQUES", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        self.frame_graph = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.frame_graph.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Colonne droite : Emprunteurs
        right_frame = ctk.CTkFrame(main_container, fg_color="#1e1e2e", corner_radius=15)
        right_frame.grid(row=0, column=1, padx=(5, 0), sticky="nsew")
        
        ctk.CTkLabel(right_frame, text="👥 PERSONNES AYANT EMPRUNTÉ", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Zone de texte pour la liste des emprunteurs
        self.emprunteurs_text = scrolledtext.ScrolledText(
            right_frame, 
            wrap="word",
            font=("Segoe UI", 12),
            bg="#1e1e2e",
            fg="#ffffff",
            relief="flat",
            borderwidth=0,
            height=20
        )
        self.emprunteurs_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuration des couleurs des tags
        self.emprunteurs_text.tag_config("title", foreground="#f39c12", font=("Segoe UI", 14, "bold"))
        self.emprunteurs_text.tag_config("name", foreground="#2ecc71", font=("Segoe UI", 11, "bold"))
        self.emprunteurs_text.tag_config("book", foreground="#3498db")
        self.emprunteurs_text.tag_config("date", foreground="#9b59b6")
        self.emprunteurs_text.tag_config("warning", foreground="#e74c3c")
        
        # Pied de page avec infos
        footer = ctk.CTkFrame(self, height=40, fg_color="#1a1a2e")
        footer.pack(fill="x", padx=10, pady=(5, 10))
        
        self.footer_label = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(size=12))
        self.footer_label.pack(pady=10)
    
    def rafraichir(self):
        """Rafraîchit les données du dashboard"""
        # Re-créer les graphiques
        self.frame_graph.destroy()
        self.frame_graph = ctk.CTkFrame(self.frame_graph.master, fg_color="transparent")
        self.frame_graph.pack(fill="both", expand=True, padx=10, pady=10)
        self.creer_graphiques()
        
        # Re-afficher la liste des emprunteurs
        self.emprunteurs_text.config(state="normal")
        self.emprunteurs_text.delete("1.0", "end")
        self.afficher_emprunteurs()
        
        messagebox.showinfo("Rafraîchissement", "Les données ont été mises à jour !")
    
    def creer_graphiques(self):
        """Crée les graphiques avec des couleurs lisibles"""
        stats = self.db.get_statistiques()
        
        # Style des graphiques
        plt.style.use('dark_background')
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5))
        fig.patch.set_facecolor('#1e1e2e')
        
        # Graphique 1: Répartition par statut
        statuts = ['Disponibles', 'Empruntés', 'Réservés']
        valeurs = [stats['disponibles'], stats['empruntes'], stats['reserves']]
        couleurs = ['#2ecc71', '#e74c3c', '#f39c12']
        explode = (0.05, 0.05, 0.05)
        
        wedges, texts, autotexts = ax1.pie(valeurs, labels=statuts, colors=couleurs, 
                                            autopct='%1.1f%%', startangle=90, explode=explode)
        
        # Personnaliser les couleurs du texte
        for text in texts:
            text.set_color('white')
            text.set_fontsize(11)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        ax1.set_title('Répartition par statut', color='white', fontsize=14, fontweight='bold')
        ax1.set_facecolor('#1e1e2e')
        
        # Graphique 2: Top 5 catégories
        categories = list(stats['categories'].items())[:5]
        noms = [c[0][:15] for c in categories]
        counts = [c[1] for c in categories]
        
        bars = ax2.bar(noms, counts, color='#9b59b6', edgecolor='white', linewidth=1)
        ax2.set_title('Top 5 catégories', color='white', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Catégories', color='white', fontsize=11)
        ax2.set_ylabel('Nombre de livres', color='white', fontsize=11)
        ax2.tick_params(colors='white')
        ax2.set_facecolor('#1e1e2e')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        
        # Ajouter les valeurs sur les barres
        for bar, val in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                    str(val), ha='center', color='white', fontsize=11, fontweight='bold')
        
        fig.tight_layout()
        
        # Intégrer dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Mettre à jour le footer
        self.footer_label.configure(
            text=f"📅 Année moyenne: {stats['annee_moyenne']} | "
                 f"🏛️ Plus ancien: {stats['plus_ancien'].titre if stats['plus_ancien'] else 'N/A'} | "
                 f"🆕 Plus récent: {stats['plus_recent'].titre if stats['plus_recent'] else 'N/A'}"
        )
    
    def afficher_emprunteurs(self):
        """Affiche la liste des personnes qui ont emprunté des livres"""
        
        # Vider le texte
        self.emprunteurs_text.config(state="normal")
        self.emprunteurs_text.delete("1.0", "end")
        
        # Récupérer les emprunts
        emprunts = self.db.lister_emprunts_en_cours()
        
        if not emprunts:
            self.emprunteurs_text.insert("end", "📭 Aucun emprunt en cours\n\n", "title")
            self.emprunteurs_text.insert("end", "Aucune personne n'a actuellement de livre emprunté.", "name")
            self.emprunteurs_text.config(state="disabled")
            return
        
        # En-tête
        self.emprunteurs_text.insert("end", f"📋 {len(emprunts)} emprunt(s) en cours\n\n", "title")
        
        # Afficher chaque emprunteur
        for i, emprunt in enumerate(emprunts, 1):
            # Vérifier si le livre est en retard
            est_en_retard = False
            if emprunt.get('date_retour'):
                try:
                    from datetime import datetime
                    date_retour = datetime.strptime(emprunt['date_retour'], "%d/%m/%Y")
                    est_en_retard = date_retour < datetime.now()
                except:
                    pass
            
            # Nom de l'emprunteur avec indicateur de retard
            if est_en_retard:
                self.emprunteurs_text.insert("end", f"{i}. ⚠️ ", "warning")
                self.emprunteurs_text.insert("end", f"{emprunt['emprunteur']}\n", "name")
            else:
                self.emprunteurs_text.insert("end", f"{i}. 👤 ", "name")
                self.emprunteurs_text.insert("end", f"{emprunt['emprunteur']}\n", "name")
            
            # Livre emprunté
            self.emprunteurs_text.insert("end", f"   📖 Livre: ", "book")
            self.emprunteurs_text.insert("end", f"{emprunt['titre']}\n", "book")
            
            # Date d'emprunt
            if emprunt.get('date_emprunt'):
                self.emprunteurs_text.insert("end", f"   📅 Emprunté le: ", "date")
                self.emprunteurs_text.insert("end", f"{emprunt['date_emprunt']}\n", "date")
            
            # Date de retour prévue
            if emprunt.get('date_retour'):
                self.emprunteurs_text.insert("end", f"   ⏰ Retour prévu: ", "date")
                if est_en_retard:
                    self.emprunteurs_text.insert("end", f"{emprunt['date_retour']} ⚠️ EN RETARD\n\n", "warning")
                else:
                    self.emprunteurs_text.insert("end", f"{emprunt['date_retour']}\n\n", "date")
            else:
                self.emprunteurs_text.insert("end", "\n", "date")
        
        # Statistiques supplémentaires
        total_emprunteurs = len(set([e['emprunteur'] for e in emprunts]))
        self.emprunteurs_text.insert("end", "━" * 40 + "\n", "date")
        self.emprunteurs_text.insert("end", f"📊 Total emprunteurs uniques: {total_emprunteurs}\n", "title")
        
        self.emprunteurs_text.config(state="disabled")
    
    def exporter_csv(self):
        """Exporte les données en CSV"""
        try:
            # Exporter les statistiques
            self.db.exporter_csv("dashboard_stats.csv")
            
            # Exporter les emprunts
            self.db.exporter_emprunts_csv("dashboard_emprunts.csv")
            
            messagebox.showinfo("Export", 
                "✅ Données exportées avec succès !\n\n"
                "📁 dashboard_stats.csv - Statistiques des livres\n"
                "📁 dashboard_emprunts.csv - Liste des emprunteurs"
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {e}")


# ==================== APPLICATION PRINCIPALE ====================

# ==================== APPLICATION PRINCIPALE ====================

class BibliothequeApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("📚 Bibliothèque Intelligente")
        self.root.geometry("1300x750")
        
        self.db = BibliothequeDB()
        self.chatbot = ChatbotIntelligent(self.db)
        self.livre_selectionne = None
        
        self.setup_ui()
        self.rafraichir_liste()
        self.root.mainloop()
    
    def setup_ui(self):
        # Barre d'outils
        toolbar = ctk.CTkFrame(self.root, height=50, fg_color="#1a1a2e")
        toolbar.pack(fill="x", padx=10, pady=(10, 5))
        toolbar.pack_propagate(False)
        
        ctk.CTkLabel(toolbar, text="📚", font=ctk.CTkFont(size=28)).pack(side="left", padx=20)
        ctk.CTkLabel(toolbar, text="BIBLIOTHÈQUE INTELLIGENTE", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        self.stats_label = ctk.CTkLabel(toolbar, text="📊 0 livres", font=ctk.CTkFont(size=12), text_color="#888")
        self.stats_label.pack(side="left", padx=20)
        
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(btn_frame, text="➕ AJOUTER", command=self.ouvrir_ajout, fg_color="#2ecc71", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="✏️ MODIFIER", command=self.ouvrir_modification, fg_color="#3498db", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="🗑️ SUPPRIMER", command=self.supprimer_livre, fg_color="#e74c3c", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📤 EMPRUNTER", command=self.ouvrir_emprunt, fg_color="#f39c12", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📥 RETOUR", command=self.ouvrir_retour, fg_color="#1abc9c", height=35, width=80).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="📊 DASHBOARD", command=self.ouvrir_dashboard, fg_color="#9b59b6", height=35, width=80).pack(side="left", padx=2)
        
        btn_backup = ctk.CTkButton(btn_frame, text="💾 BACKUP", command=self.faire_backup, 
                                fg_color="#2c3e50", hover_color="#1a252f", height=35, width=70)
        btn_backup.pack(side="left", padx=2)

        btn_restore = ctk.CTkButton(btn_frame, text="🔄 RESTORE", command=self.restaurer_backup, 
                                    fg_color="#e67e22", hover_color="#d35400", height=35, width=70)
        btn_restore.pack(side="left", padx=2)
        
        # Recherche
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        self.entry_recherche = ctk.CTkEntry(search_frame, placeholder_text="🔍 Rechercher...", width=250)
        self.entry_recherche.pack(side="left", padx=5)
        self.entry_recherche.bind("<Return>", lambda e: self.rechercher())
        ctk.CTkButton(search_frame, text="Chercher", command=self.rechercher, width=60).pack(side="left", padx=2)
        ctk.CTkButton(search_frame, text="Tous", command=self.rafraichir_liste, width=50).pack(side="left", padx=2)
        
        # Onglets
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        tab_catalogue = self.tabview.add("📚 CATALOGUE")
        tab_chatbot = self.tabview.add("🤖 CHATBOT")
        
        # Tableau des livres
        tree_frame = ctk.CTkFrame(tab_catalogue, fg_color="#0f0f1a")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, selectmode="browse")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#1e1e2e", foreground="white", fieldbackground="#1e1e2e", rowheight=35)
        style.configure("Treeview.Heading", background="#1a1a2e", foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])
        
        columns = ("ID", "TITRE", "AUTEUR", "CATÉGORIE", "ANNÉE", "QTY", "STATUT")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        self.tree.column("ID", width=60, anchor="center")
        self.tree.column("TITRE", width=400, anchor="w")
        self.tree.column("AUTEUR", width=200, anchor="w")
        self.tree.column("CATÉGORIE", width=130, anchor="w")
        self.tree.column("ANNÉE", width=70, anchor="center")
        self.tree.column("QTY", width=60, anchor="center")
        self.tree.column("STATUT", width=110, anchor="center")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("TITRE", text="TITRE")
        self.tree.heading("AUTEUR", text="AUTEUR")
        self.tree.heading("CATÉGORIE", text="CATÉGORIE")
        self.tree.heading("ANNÉE", text="ANNÉE")
        self.tree.heading("QTY", text="QTY")
        self.tree.heading("STATUT", text="STATUT")
        
        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Chatbot
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
        
        self.chat_display.insert("end", "🤖 Bienvenue ! Je suis votre assistant.\n\n", "bot")
        self.chat_display.insert("end", "💡 Exemples de questions :\n", "bot")
        self.chat_display.insert("end", "   • 'livres disponibles'\n", "bot")
        self.chat_display.insert("end", "   • 'ID 2 existe ?'\n", "bot")
        self.chat_display.insert("end", "   • 'Victor Hugo'\n", "bot")
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.livre_selectionne = int(selected[0])
        else:
            self.livre_selectionne = None
    
    def afficher_livres_dans_tree(self, livres):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for livre in livres:
            statut_text = {"disponible": f"✅ {livre.statut.upper()}", 
                          "emprunté": f"📤 {livre.statut.upper()}", 
                          "réservé": f"🔒 {livre.statut.upper()}"}.get(livre.statut, livre.statut.upper())
            self.tree.insert("", "end", iid=str(livre.id_livre), values=(
                livre.id_livre, livre.titre[:50], livre.auteur[:25], 
                livre.categorie[:15], livre.annee_publication, 
                livre.quantite_disponible, statut_text
            ))
        total = len(livres)
        dispo = len([l for l in livres if l.statut == "disponible"])
        self.stats_label.configure(text=f"📊 {total} livres • ✅ {dispo} dispo")
    
    def rafraichir_liste(self):
        self.afficher_livres_dans_tree(self.db.afficher_tous_les_livres())
    
    def supprimer_livre(self):
        if not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre")
            return
        livre = self.db.rechercher_par_id(self.livre_selectionne)
        if messagebox.askyesno("Confirmation", f"Supprimer '{livre.titre}' ?"):
            self.db.supprimer_livre(self.livre_selectionne)
            self.rafraichir_liste()
            self.livre_selectionne = None
            messagebox.showinfo("Succès", "Livre supprimé")
    
    def ouvrir_ajout(self):
        AjouterLivreDialog(self.root, self.apres_ajout)
    
    def apres_ajout(self, livre):
        self.db.ajouter_livre(livre)
        self.rafraichir_liste()
        messagebox.showinfo("Succès", f"Livre '{livre.titre}' ajouté")
    
    def ouvrir_modification(self):
        if not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre")
            return
        livre = self.db.rechercher_par_id(self.livre_selectionne)
        ModifierLivreDialog(self.root, livre, self.apres_modification)
    
    def apres_modification(self, id_livre, modifications):
        self.db.modifier_livre(id_livre, **modifications)
        self.rafraichir_liste()
        self.livre_selectionne = None
        messagebox.showinfo("Succès", "Livre modifié")
    
    def ouvrir_emprunt(self):
        if not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre")
            return
        livre = self.db.rechercher_par_id(self.livre_selectionne)
        if livre.statut != "disponible":
            messagebox.showwarning("Impossible", f"Ce livre n'est pas disponible (statut: {livre.statut})")
            return
        
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Emprunter")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text=f"Emprunter : {livre.titre}", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
        ctk.CTkLabel(dialog, text="Nom :").pack()
        entry_nom = ctk.CTkEntry(dialog, width=250)
        entry_nom.pack(pady=5)
        ctk.CTkLabel(dialog, text="Durée (jours) :").pack()
        combo = ctk.CTkComboBox(dialog, values=["7", "14", "21", "30"])
        combo.set("14")
        combo.pack(pady=5)
        
        def valider():
            nom = entry_nom.get().strip() or "Anonyme"
            duree = int(combo.get())
            self.db.emprunter_livre(livre.id_livre, nom, duree)
            self.rafraichir_liste()
            self.livre_selectionne = None
            dialog.destroy()
            messagebox.showinfo("Succès", f"Livre emprunté pour {duree} jours")
        
        ctk.CTkButton(dialog, text="CONFIRMER", command=valider, fg_color="#2ecc71").pack(pady=20)
    
    def ouvrir_retour(self):
        if not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre")
            return
        livre = self.db.rechercher_par_id(self.livre_selectionne)
        if livre.statut != "emprunté":
            messagebox.showwarning("Impossible", "Ce livre n'est pas emprunté")
            return
        if messagebox.askyesno("Confirmation", f"Retour de '{livre.titre}' ?"):
            self.db.retourner_livre(livre.id_livre)
            self.rafraichir_liste()
            self.livre_selectionne = None
            messagebox.showinfo("Succès", "Livre retourné")
    
    def ouvrir_dashboard(self):
        DashboardStatistiques(self.root, self.db)
    
    def faire_backup(self):
        msg = self.db.backup_database()
        messagebox.showinfo("Backup", msg)

    def restaurer_backup(self):
        """Restaure une sauvegarde sélectionnée par l'utilisateur"""
        success, message = self.db.restaurer_backup_interactif()
        if success:
            self.rafraichir_liste()
            self.livre_selectionne = None
            messagebox.showinfo("Succès", message)
        else:
            messagebox.showerror("Erreur", message)

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
    
    def rechercher(self):
        terme = self.entry_recherche.get().strip()
        if not terme:
            self.rafraichir_liste()
            return
        resultats = []
        if terme.isdigit():
            l = self.db.rechercher_par_id(int(terme))
            if l:
                resultats.append(l)
        else:
            resultats = self.db.rechercher_par_titre(terme)
            for l in self.db.rechercher_par_auteur(terme):
                if l not in resultats:
                    resultats.append(l)
        self.afficher_livres_dans_tree(resultats)
        if not resultats:
            messagebox.showinfo("Résultat", f"Aucun résultat pour '{terme}'")


if __name__ == "__main__":
    print("="*60)
    print("📚 BIBLIOTHÈQUE INTELLIGENTE")
    print("="*60)
    app = BibliothequeApp()
    
def restaurer_backup(self):   # <-- AJOUTE CETTE MÉTHODE ICI
    """Restaure une sauvegarde sélectionnée par l'utilisateur"""
    success, message = self.db.restaurer_backup_interactif()
    if success:
        self.rafraichir_liste()
        self.livre_selectionne = None
        messagebox.showinfo("Succès", message)
    else:
        messagebox.showerror("Erreur", message)



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
    
    def rechercher(self):
        terme = self.entry_recherche.get().strip()
        if not terme:
            self.rafraichir_liste()
            return
        resultats = []
        if terme.isdigit():
            l = self.db.rechercher_par_id(int(terme))
            if l:
                resultats.append(l)
        else:
            resultats = self.db.rechercher_par_titre(terme)
            for l in self.db.rechercher_par_auteur(terme):
                if l not in resultats:
                    resultats.append(l)
        self.afficher_livres_dans_tree(resultats)
        if not resultats:
            messagebox.showinfo("Résultat", f"Aucun résultat pour '{terme}'")


if __name__ == "__main__":
    print("="*60)
    print("📚 BIBLIOTHÈQUE INTELLIGENTE")
    print("="*60)
    app = BibliothequeApp()