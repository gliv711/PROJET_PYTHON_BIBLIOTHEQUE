# database.py
# Gestion de la base de données SQLite - CRUD complet + emprunts + statistiques

import sqlite3
import csv
from datetime import datetime, timedelta
from models import Livre
from config import get_db_path

class BibliothequeDB:
    """
    Classe qui gère toutes les opérations sur la base de données
    CRUD complet + emprunts + export + statistiques
    """
    
    def __init__(self):
        """Initialise la connexion à la base et crée la table si elle n'existe pas"""
        self.db_path = get_db_path()
        self.init_database()
    
    def init_database(self):
        """Crée la table des livres avec tous les champs demandés"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS livres (
                id_livre INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                categorie TEXT NOT NULL,
                annee_publication INTEGER NOT NULL,
                quantite_disponible INTEGER NOT NULL DEFAULT 1,
                statut TEXT NOT NULL DEFAULT 'disponible',
                date_retour_prevue TEXT,
                date_emprunt TEXT,
                emprunteur TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée avec succès")
    
    # ==================== CRUD PRINCIPAL ====================
    
    def ajouter_livre(self, livre):
        """Ajouter un nouveau livre dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO livres (titre, auteur, categorie, annee_publication, 
                               quantite_disponible, statut, date_retour_prevue)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', livre.to_tuple())
        
        livre.id_livre = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"✅ Livre ajouté : {livre.titre} (ID: {livre.id_livre})")
        return livre.id_livre
    
    def afficher_tous_les_livres(self):
        """Récupère et retourne tous les livres de la bibliothèque"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres ORDER BY titre')
        rows = cursor.fetchall()
        conn.close()
        
        livres = []
        for row in rows:
            livre = Livre(
                id_livre=row[0],
                titre=row[1],
                auteur=row[2],
                categorie=row[3],
                annee_publication=row[4],
                quantite_disponible=row[5],
                statut=row[6],
                date_retour_prevue=row[7]
            )
            livres.append(livre)
        
        return livres
    
    def modifier_livre(self, id_livre, **champs_modifies):
        """Modifier les informations d'un livre"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        set_clauses = []
        valeurs = []
        
        for champ, valeur in champs_modifies.items():
            set_clauses.append(f"{champ} = ?")
            valeurs.append(valeur)
        
        valeurs.append(id_livre)
        query = f"UPDATE livres SET {', '.join(set_clauses)} WHERE id_livre = ?"
        
        cursor.execute(query, valeurs)
        conn.commit()
        conn.close()
        
        print(f"✅ Livre ID {id_livre} modifié")
        return cursor.rowcount > 0
    
    def supprimer_livre(self, id_livre):
        """Supprimer un livre par son ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM livres WHERE id_livre = ?', (id_livre,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Livre ID {id_livre} supprimé")
        return cursor.rowcount > 0
    
    # ==================== GESTION DES EMPRUNTS ====================
    
    def emprunter_livre(self, id_livre, emprunteur="Anonyme", jours_emprunt=14):
        """Emprunte un livre pour X jours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si le livre existe et est disponible
        cursor.execute('SELECT quantite_disponible, statut, titre FROM livres WHERE id_livre = ?', (id_livre,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Livre non trouvé"
        
        quantite, statut, titre = result
        
        if quantite <= 0 or statut != "disponible":
            conn.close()
            return False, f"Le livre '{titre}' n'est pas disponible pour l'emprunt"
        
        date_emprunt = datetime.now().strftime("%d/%m/%Y")
        date_retour = (datetime.now() + timedelta(days=jours_emprunt)).strftime("%d/%m/%Y")
        
        nouvelle_quantite = quantite - 1
        nouveau_statut = "emprunté" if nouvelle_quantite == 0 else "disponible"
        
        cursor.execute('''
            UPDATE livres 
            SET quantite_disponible = ?,
                statut = ?,
                date_retour_prevue = ?,
                date_emprunt = ?,
                emprunteur = ?
            WHERE id_livre = ?
        ''', (nouvelle_quantite, nouveau_statut, date_retour, date_emprunt, emprunteur, id_livre))
        
        conn.commit()
        conn.close()
        
        return True, f"✅ Livre '{titre}' emprunté avec succès ! Retour prévu le {date_retour}"
    
    def retourner_livre(self, id_livre):
        """Retourne un livre emprunté"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Vérifier si le livre existe
        cursor.execute('SELECT quantite_disponible, titre, statut FROM livres WHERE id_livre = ?', (id_livre,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False, "Livre non trouvé"
        
        quantite, titre, statut = result
        
        if statut == "disponible":
            conn.close()
            return False, f"Le livre '{titre}' n'est pas emprunté"
        
        nouvelle_quantite = quantite + 1
        nouveau_statut = "disponible"
        
        cursor.execute('''
            UPDATE livres 
            SET quantite_disponible = ?,
                statut = ?,
                date_retour_prevue = NULL,
                date_emprunt = NULL,
                emprunteur = NULL
            WHERE id_livre = ?
        ''', (nouvelle_quantite, nouveau_statut, id_livre))
        
        conn.commit()
        conn.close()
        
        return True, f"✅ Livre '{titre}' retourné avec succès ! Merci !"
    
    def lister_emprunts_en_cours(self):
        """Liste tous les livres actuellement empruntés (basé sur champ emprunteur)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Récupérer tous les livres qui ont un emprunteur (peu importe le statut)
        cursor.execute('''
            SELECT id_livre, titre, auteur, date_retour_prevue, date_emprunt, emprunteur
            FROM livres 
            WHERE emprunteur IS NOT NULL 
            AND emprunteur != ''
            ORDER BY date_retour_prevue
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        emprunts = []
        for row in rows:
            emprunts.append({
                'id': row[0],
                'titre': row[1],
                'auteur': row[2],
                'date_retour': row[3],
                'date_emprunt': row[4],
                'emprunteur': row[5] or "Anonyme"
            })
        
        return emprunts
    
    def verifier_retards(self):
        """Vérifie les livres en retard"""
        aujourdhui = datetime.now().strftime("%d/%m/%Y")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id_livre, titre, auteur, date_retour_prevue, emprunteur
            FROM livres 
            WHERE emprunteur IS NOT NULL 
            AND emprunteur != ''
            AND date_retour_prevue < ?
        ''', (aujourdhui,))
        
        rows = cursor.fetchall()
        conn.close()
        
        retards = []
        for row in rows:
            retards.append({
                'id': row[0],
                'titre': row[1],
                'auteur': row[2],
                'date_retour': row[3],
                'emprunteur': row[4] or "Anonyme"
            })
        
        return retards
    
    # ==================== RECHERCHES ====================
    
    def rechercher_par_id(self, id_livre):
        """Rechercher un livre par son ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres WHERE id_livre = ?', (id_livre,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Livre(
                id_livre=row[0],
                titre=row[1],
                auteur=row[2],
                categorie=row[3],
                annee_publication=row[4],
                quantite_disponible=row[5],
                statut=row[6],
                date_retour_prevue=row[7]
            )
        return None
    
    def rechercher_par_titre(self, titre):
        """Rechercher des livres par titre (recherche partielle)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres WHERE titre LIKE ?', (f'%{titre}%',))
        rows = cursor.fetchall()
        conn.close()
        
        livres = []
        for row in rows:
            livres.append(Livre(
                id_livre=row[0], titre=row[1], auteur=row[2],
                categorie=row[3], annee_publication=row[4],
                quantite_disponible=row[5], statut=row[6], date_retour_prevue=row[7]
            ))
        return livres
    
    def rechercher_par_auteur(self, auteur):
        """Rechercher des livres par auteur (recherche partielle)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres WHERE auteur LIKE ?', (f'%{auteur}%',))
        rows = cursor.fetchall()
        conn.close()
        
        livres = []
        for row in rows:
            livres.append(Livre(
                id_livre=row[0], titre=row[1], auteur=row[2],
                categorie=row[3], annee_publication=row[4],
                quantite_disponible=row[5], statut=row[6], date_retour_prevue=row[7]
            ))
        return livres
    
    def filtrer_par_categorie(self, categorie):
        """Filtre les livres par catégorie"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres WHERE categorie LIKE ?', (f'%{categorie}%',))
        rows = cursor.fetchall()
        conn.close()
        
        livres = []
        for row in rows:
            livres.append(Livre(
                id_livre=row[0], titre=row[1], auteur=row[2],
                categorie=row[3], annee_publication=row[4],
                quantite_disponible=row[5], statut=row[6], date_retour_prevue=row[7]
            ))
        return livres
    
    def filtrer_par_annee(self, annee_min, annee_max):
        """Filtre les livres par plage d'années"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM livres WHERE annee_publication BETWEEN ? AND ?', (annee_min, annee_max))
        rows = cursor.fetchall()
        conn.close()
        
        livres = []
        for row in rows:
            livres.append(Livre(
                id_livre=row[0], titre=row[1], auteur=row[2],
                categorie=row[3], annee_publication=row[4],
                quantite_disponible=row[5], statut=row[6], date_retour_prevue=row[7]
            ))
        return livres
    
    # ==================== STATISTIQUES ====================
    
    def get_statistiques(self):
        """Retourne des statistiques complètes sur la bibliothèque"""
        livres = self.afficher_tous_les_livres()
        
        total = len(livres)
        disponibles = len([l for l in livres if l.statut == "disponible"])
        empruntes = len([l for l in livres if l.statut == "emprunté"])
        reserves = len([l for l in livres if l.statut == "réservé"])
        
        # Statistiques par catégorie
        categories = {}
        for livre in livres:
            if livre.categorie in categories:
                categories[livre.categorie] += 1
            else:
                categories[livre.categorie] = 1
        
        # Année moyenne
        if total > 0:
            annee_moyenne = sum([l.annee_publication for l in livres]) // total
        else:
            annee_moyenne = 0
        
        # Livre le plus ancien et le plus récent
        if livres:
            plus_ancien = min(livres, key=lambda x: x.annee_publication)
            plus_recent = max(livres, key=lambda x: x.annee_publication)
        else:
            plus_ancien = plus_recent = None
        
        return {
            'total': total,
            'disponibles': disponibles,
            'empruntes': empruntes,
            'reserves': reserves,
            'categories': categories,
            'annee_moyenne': annee_moyenne,
            'plus_ancien': plus_ancien,
            'plus_recent': plus_recent
        }
    
    # ==================== EXPORT ====================
    
    def exporter_csv(self, filename="catalogue_bibliotheque.csv"):
        """Exporte le catalogue complet en CSV"""
        livres = self.afficher_tous_les_livres()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Titre', 'Auteur', 'Catégorie', 'Année', 'Quantité', 'Statut', 'Date retour'])
            
            for livre in livres:
                writer.writerow([
                    livre.id_livre, livre.titre, livre.auteur, 
                    livre.categorie, livre.annee_publication, 
                    livre.quantite_disponible, livre.statut,
                    livre.date_retour_prevue or ""
                ])
        
        return f"✅ Exporté vers {filename}"
    
    def exporter_emprunts_csv(self, filename="emprunts_en_cours.csv"):
        """Exporte la liste des emprunts en CSV"""
        emprunts = self.lister_emprunts_en_cours()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Titre', 'Auteur', 'Emprunteur', "Date d'emprunt", 'Retour prévu'])
            
            for emprunt in emprunts:
                writer.writerow([
                    emprunt['id'], emprunt['titre'], emprunt['auteur'],
                    emprunt['emprunteur'], emprunt['date_emprunt'], emprunt['date_retour']
                ])
        
        return f"✅ Exporté vers {filename}"
    
    # ==================== SAUVEGARDE ====================
    
    def backup_database(self, backup_name=None):
        """Sauvegarde la base de données"""
        import shutil
        import os
        
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_bibliotheque_{timestamp}.db"
        
        shutil.copy2(self.db_path, backup_name)
        return f"✅ Base de données sauvegardée vers {backup_name}"
    
    def restaurer_backup_interactif(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier backup et le restaurer"""
        from tkinter import filedialog
        import os
        import shutil
        
        # Ouvrir la boîte de dialogue pour choisir un fichier
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier de sauvegarde",
            filetypes=[("Base de données SQLite", "*.db"), ("Tous les fichiers", "*.*")],
            initialdir="."
        )
        
        if not filename:
            return False, "Aucun fichier sélectionné"
        
        if not os.path.exists(filename):
            return False, f"Fichier {filename} non trouvé"
        
        try:
            # Vérifier que c'est bien une base SQLite
            test_conn = sqlite3.connect(filename)
            test_conn.cursor().execute("SELECT name FROM sqlite_master WHERE type='table'")
            test_conn.close()
            
            # Faire une copie de sauvegarde avant restauration
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            auto_backup = f"auto_backup_before_restore_{timestamp}.db"
            shutil.copy2(self.db_path, auto_backup)
            
            # Restaurer le fichier sélectionné
            shutil.copy2(filename, self.db_path)
            
            return True, f"✅ Base restaurée depuis {os.path.basename(filename)}\n\n📁 Sauvegarde automatique créée: {auto_backup}"
            
        except Exception as e:
            return False, f"❌ Erreur lors de la restauration: {str(e)}"
    
    def restaurer_backup(self, backup_path):
        """Restaure une sauvegarde (méthode avec chemin direct)"""
        import shutil
        import os
        
        if not os.path.exists(backup_path):
            return False, f"Fichier {backup_path} non trouvé"
        
        shutil.copy2(backup_path, self.db_path)
        return True, f"✅ Restauration depuis {backup_path} effectuée"
    
    # ==================== GESTION DES CATÉGORIES ====================
    
    def get_toutes_categories(self):
        """Retourne la liste de toutes les catégories existantes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT categorie FROM livres ORDER BY categorie')
        rows = cursor.fetchall()
        conn.close()
        
        return [row[0] for row in rows]
    
    def ajouter_categorie(self, categorie):
        """Ajoute une catégorie (vérification d'existence)"""
        categories = self.get_toutes_categories()
        if categorie not in categories:
            return f"📌 La catégorie '{categorie}' sera disponible lors de l'ajout d'un livre"
        return f"⚠️ La catégorie '{categorie}' existe déjà"
    
    # ==================== DONNÉES DE TEST ====================
    
    def ajouter_donnees_test(self):
        """Ajoute des livres d'exemple (pour tester l'application)"""
        livres_test = [
            Livre(titre="Le Petit Prince", auteur="Antoine de Saint-Exupéry", 
                  categorie="Roman", annee_publication=1943, quantite_disponible=3, statut="disponible"),
            Livre(titre="Les Misérables", auteur="Victor Hugo", 
                  categorie="Roman", annee_publication=1862, quantite_disponible=0, 
                  statut="emprunté", date_retour_prevue="15/03/2026"),
            Livre(titre="Notre-Dame de Paris", auteur="Victor Hugo", 
                  categorie="Roman", annee_publication=1831, quantite_disponible=2, statut="disponible"),
            Livre(titre="Orgueil et Préjugés", auteur="Jane Austen", 
                  categorie="Roman romantique", annee_publication=1813, quantite_disponible=1, statut="disponible"),
            Livre(titre="Jane Eyre", auteur="Charlotte Brontë", 
                  categorie="Roman romantique", annee_publication=1847, quantite_disponible=1, statut="disponible"),
            Livre(titre="Le Rouge et le Noir", auteur="Stendhal", 
                  categorie="Roman", annee_publication=1830, quantite_disponible=0, statut="emprunté"),
            Livre(titre="Introduction à l'IA", auteur="Stuart Russell", 
                  categorie="Informatique", annee_publication=2010, quantite_disponible=2, statut="disponible"),
            Livre(titre="Histoire de France", auteur="Jules Michelet", 
                  categorie="Histoire", annee_publication=1855, quantite_disponible=1, statut="réservé"),
        ]
        
        for livre in livres_test:
            self.ajouter_livre(livre)
        
        print("📚 Données de test ajoutées avec succès !")