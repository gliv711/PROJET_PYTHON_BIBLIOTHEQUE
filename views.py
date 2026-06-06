# views.py - Toutes les vues de l'application

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
from styles import COLORS
from database import BibliothequeDB
from models import Livre

class BaseView(ctk.CTkFrame):
    """Vue de base avec barre de navigation"""
    
    def __init__(self, parent, nav_manager, title, **kwargs):
        super().__init__(parent, fg_color=COLORS["darker"], **kwargs)
        self.nav_manager = nav_manager
        self.title = title
        self.db = BibliothequeDB()
        
        self.setup_header()
    
    def setup_header(self):
        """Configure l'en-tête avec le titre et les boutons de navigation"""
        header = ctk.CTkFrame(self, height=60, fg_color=COLORS["dark"])
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # Bouton retour
        back_btn = ctk.CTkButton(
            header, 
            text="← RETOUR", 
            command=self.nav_manager.go_back,
            fg_color=COLORS["secondary"],
            hover_color=COLORS["secondary_dark"],
            width=100, 
            height=35
        )
        back_btn.pack(side="left", padx=20)
        
        # Titre
        ctk.CTkLabel(
            header, 
            text=self.title, 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", padx=20)


class CatalogueView(BaseView):
    """Vue du catalogue des livres"""
    
    def __init__(self, parent, nav_manager):
        super().__init__(parent, nav_manager, "📚 CATALOGUE DES LIVRES")
        self.livre_selectionne = None
        self.setup_ui()
        self.rafraichir_liste()
    
    def setup_ui(self):
        """Interface du catalogue"""
        
        # Barre d'outils
        toolbar = ctk.CTkFrame(self, height=50, fg_color=COLORS["light"])
        toolbar.pack(fill="x", padx=10, pady=10)
        
        # Statistiques
        self.stats_label = ctk.CTkLabel(toolbar, text="📊 0 livres", font=ctk.CTkFont(size=12))
        self.stats_label.pack(side="left", padx=20)
        
        # Boutons d'actions
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        buttons = [
            ("➕ AJOUTER", self.ouvrir_ajout, COLORS["primary"]),
            ("✏️ MODIFIER", self.ouvrir_modification, COLORS["secondary"]),
            ("🗑️ SUPPRIMER", self.supprimer_livre, COLORS["danger"]),
            ("📤 EMPRUNTER", self.ouvrir_emprunt, COLORS["warning"]),
            ("📥 RETOUR", self.ouvrir_retour, COLORS["success"])
        ]
        
        for text, command, color in buttons:
            ctk.CTkButton(
                btn_frame, text=text, command=command,
                fg_color=color, height=35, width=90
            ).pack(side="left", padx=2)
        
        # Recherche
        search_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        search_frame.pack(side="right", padx=20)
        
        self.entry_recherche = ctk.CTkEntry(search_frame, placeholder_text="🔍 Rechercher...", width=250)
        self.entry_recherche.pack(side="left", padx=5)
        self.entry_recherche.bind("<Return>", lambda e: self.rechercher())
        
        ctk.CTkButton(search_frame, text="Chercher", command=self.rechercher, width=60).pack(side="left", padx=2)
        ctk.CTkButton(search_frame, text="Tous", command=self.rafraichir_liste, width=50).pack(side="left", padx=2)
        
        # Tableau
        tree_frame = ctk.CTkFrame(self, fg_color=COLORS["darker"])
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tree = ttk.Treeview(tree_frame, selectmode="browse")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=COLORS["light"], foreground="white", 
                       fieldbackground=COLORS["light"], rowheight=35)
        style.configure("Treeview.Heading", background=COLORS["dark"], foreground="white", 
                       font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', COLORS["secondary"])])
        
        columns = ("ID", "TITRE", "AUTEUR", "CATÉGORIE", "ANNÉE", "QTY", "STATUT")
        self.tree["columns"] = columns
        self.tree["show"] = "headings"
        
        widths = [60, 400, 200, 130, 70, 60, 110]
        for col, w in zip(columns, widths):
            self.tree.column(col, width=w, anchor="center" if col != "TITRE" else "w")
            self.tree.heading(col, text=col)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Info sélection
        info_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        info_frame.pack(fill="x", padx=10, pady=5)
        self.info_label = ctk.CTkLabel(info_frame, text="💡 Cliquez sur un livre pour le sélectionner", 
                                       text_color=COLORS["text_secondary"])
        self.info_label.pack()
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.livre_selectionne = int(selected[0])
            livre = self.db.rechercher_par_id(self.livre_selectionne)
            if livre:
                self.info_label.configure(text=f"✅ Livre sélectionné : ID {livre.id_livre} - {livre.titre}",
                                         text_color=COLORS["success"])
    
    def afficher_livres_dans_tree(self, livres):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for livre in livres:
            statut_text = {
                "disponible": f"✅ {livre.statut.upper()}",
                "emprunté": f"📤 {livre.statut.upper()}",
                "réservé": f"🔒 {livre.statut.upper()}"
            }.get(livre.statut, livre.statut.upper())
            
            self.tree.insert("", "end", iid=str(livre.id_livre), values=(
                livre.id_livre, livre.titre[:50], livre.auteur[:25],
                livre.categorie[:15], livre.annee_publication,
                livre.quantite_disponible, statut_text
            ))
        
        total = len(livres)
        dispo = len([l for l in livres if l.statut == "disponible"])
        self.stats_label.configure(text=f"📊 {total} livres • ✅ {dispo} disponibles")
    
    def rafraichir_liste(self):
        self.afficher_livres_dans_tree(self.db.afficher_tous_les_livres())
    
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
        AjouterLivreDialog(self, self.apres_ajout)
    
    def apres_ajout(self, livre):
        self.db.ajouter_livre(livre)
        self.rafraichir_liste()
        messagebox.showinfo("Succès", f"Livre '{livre.titre}' ajouté")
    
    def ouvrir_modification(self):
        if not self.livre_selectionne:
            messagebox.showwarning("Attention", "Sélectionnez un livre")
            return
        livre = self.db.rechercher_par_id(self.livre_selectionne)
        ModifierLivreDialog(self, livre, self.apres_modification)
    
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
            messagebox.showwarning("Impossible", f"Ce livre n'est pas disponible")
            return
        
        dialog = ctk.CTkToplevel(self)
        dialog.title("Emprunter")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrer
        x = self.winfo_rootx() + (self.winfo_width() - 400) // 2
        y = self.winfo_rooty() + (self.winfo_height() - 300) // 2
        dialog.geometry(f"+{x}+{y}")
        
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
        
        ctk.CTkButton(dialog, text="CONFIRMER", command=valider, fg_color=COLORS["primary"]).pack(pady=20)
    
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


class DashboardView(BaseView):
    """Vue du dashboard avec graphiques"""
    
    def __init__(self, parent, nav_manager):
        super().__init__(parent, nav_manager, "📊 DASHBOARD STATISTIQUES")
        self.setup_ui()
        self.charger_donnees()
    
    def setup_ui(self):
        """Interface du dashboard"""
        
        # Barre d'outils
        toolbar = ctk.CTkFrame(self, height=50, fg_color=COLORS["light"])
        toolbar.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            toolbar, text="🔄 RAFRAÎCHIR", command=self.charger_donnees,
            fg_color=COLORS["secondary"], width=120
        ).pack(side="left", padx=20)
        
        ctk.CTkButton(
            toolbar, text="📁 EXPORT CSV", command=self.exporter_csv,
            fg_color=COLORS["primary"], width=120
        ).pack(side="left", padx=10)
        
        # Conteneur des graphiques
        self.graph_frame = ctk.CTkFrame(self, fg_color=COLORS["light"], corner_radius=15)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Label de chargement
        self.loading_label = ctk.CTkLabel(self.graph_frame, text="⏳ Chargement des données...", 
                                          font=ctk.CTkFont(size=16))
        self.loading_label.pack(expand=True)
    
    def charger_donnees(self):
        """Charge et affiche les données avec animation"""
        self.loading_label.pack(expand=True)
        self.graph_frame.update()
        
        # Simuler un temps de chargement
        self.after(500, self.creer_graphiques)
    
    def creer_graphiques(self):
        """Crée les graphiques"""
        self.loading_label.pack_forget()
        
        stats = self.db.get_statistiques()
        
        plt.style.use('dark_background')
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.patch.set_facecolor(COLORS["light"])
        
        # Camembert
        statuts = ['Disponibles', 'Empruntés', 'Réservés']
        valeurs = [stats['disponibles'], stats['empruntes'], stats['reserves']]
        couleurs = ['#2ecc71', '#e74c3c', '#f39c12']
        ax1.pie(valeurs, labels=statuts, colors=couleurs, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Répartition par statut', color='white', fontsize=14, fontweight='bold')
        ax1.set_facecolor(COLORS["light"])
        
        # Barres
        categories = list(stats['categories'].items())[:5]
        noms = [c[0][:15] for c in categories]
        counts = [c[1] for c in categories]
        
        bars = ax2.bar(noms, counts, color='#9b59b6', edgecolor='white')
        ax2.set_title('Top 5 catégories', color='white', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Catégories', color='white')
        ax2.set_ylabel('Nombre de livres', color='white')
        ax2.tick_params(colors='white')
        ax2.set_facecolor(COLORS["light"])
        
        for bar, val in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(val), ha='center', color='white', fontweight='bold')
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Informations
        info_text = f"""
        📊 STATISTIQUES GÉNÉRALES:
        • Total livres: {stats['total']}
        • Année moyenne: {stats['annee_moyenne']}
        • Plus ancien: {stats['plus_ancien'].titre if stats['plus_ancien'] else 'N/A'}
        • Plus récent: {stats['plus_recent'].titre if stats['plus_recent'] else 'N/A'}
        """
        
        info_frame = ctk.CTkFrame(self, fg_color=COLORS["light"], corner_radius=10)
        info_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(info_frame, text=info_text, font=ctk.CTkFont(size=12), 
                    justify="left").pack(pady=10)
    
    def exporter_csv(self):
        try:
            self.db.exporter_csv("dashboard_stats.csv")
            messagebox.showinfo("Export", "✅ Données exportées vers dashboard_stats.csv")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))


class ChatbotView(BaseView):
    """Vue du chatbot"""
    
    def __init__(self, parent, nav_manager):
        super().__init__(parent, nav_manager, "🤖 CHATBOT INTELLIGENT")
        self.chatbot = None
        self.setup_ui()
        self.init_chatbot()
    
    def setup_ui(self):
        """Interface du chatbot"""
        
        # Zone de chat
        chat_container = ctk.CTkFrame(self, fg_color=COLORS["light"], corner_radius=15)
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_container, wrap="word", font=("Segoe UI", 11),
            bg=COLORS["light"], fg="white", relief="flat"
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.tag_config("bot", foreground="#9b59b6")
        self.chat_display.tag_config("user", foreground="#3498db")
        
        # Zone de saisie
        input_frame = ctk.CTkFrame(chat_container, fg_color="transparent")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.entry_chat = ctk.CTkEntry(input_frame, placeholder_text="💬 Posez votre question...", height=45)
        self.entry_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry_chat.bind("<Return>", lambda e: self.envoyer_message())
        
        self.btn_envoyer = ctk.CTkButton(
            input_frame, text="ENVOYER", command=self.envoyer_message,
            fg_color=COLORS["info"], height=45
        )
        self.btn_envoyer.pack(side="right")
        
        self.chat_display.insert("end", "🤖 Bienvenue ! Je suis votre assistant.\n\n", "bot")
        self.chat_display.insert("end", "💡 Exemples de questions :\n", "bot")
        self.chat_display.insert("end", "   • 'livres disponibles'\n", "bot")
        self.chat_display.insert("end", "   • 'ID 2 existe ?'\n", "bot")
        self.chat_display.insert("end", "   • 'Victor Hugo'\n", "bot")
    
    def init_chatbot(self):
        """Initialise le chatbot"""
        self.loading_label = ctk.CTkLabel(self, text="⏳ Initialisation du chatbot...", font=ctk.CTkFont(size=14))
        self.loading_label.pack(pady=20)
        self.update()
        
        def load():
            from chatbot import ChatbotIntelligent
            self.chatbot = ChatbotIntelligent(self.db)
            self.loading_label.destroy()
        
        self.after(100, load)
    
    def envoyer_message(self):
        message = self.entry_chat.get().strip()
        if not message:
            return
        
        self.chat_display.insert("end", f"\n👤 {message}\n", "user")
        self.entry_chat.delete(0, "end")
        self.update()
        
        if self.chatbot:
            reponse = self.chatbot.get_reponse(message)
            self.chat_display.insert("end", f"🤖 {reponse}\n", "bot")
        else:
            self.chat_display.insert("end", "🤖 Chatbot en cours d'initialisation...\n", "bot")
        
        self.chat_display.see("end")


# Popups (inchangés mais fonctionnels)
class AjouterLivreDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.callback = callback
        self.title("📖 Ajouter un livre")
        self.geometry("500x550")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        x = parent.winfo_rootx() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 550) // 2
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
        
        x = parent.winfo_rootx() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 550) // 2
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