
import sqlite3
from models import Livre
from config import get_db_path

class BibliothequeDB:
    """
    Classe qui gère toutes les opérations sur la base de données
    CRUD complet conforme au cahier des charges
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
                date_retour_prevue TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée avec succès")
    
    # ==================== CRUD PRINCIPAL ====================
    
    def ajouter_livre(self, livre):
        """
        Ajouter un nouveau livre dans la base de données
        """
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
        """
        Récupère et retourne tous les livres de la bibliothèque
        """
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
        """
        Modifier les informations d'un livre
        Exemple: modifier_livre(1, titre="Nouveau titre", quantite_disponible=5)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construire la requête dynamiquement
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
        """
        Supprimer un livre par son ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM livres WHERE id_livre = ?', (id_livre,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Livre ID {id_livre} supprimé")
        return cursor.rowcount > 0
    
    # ==================== RECHERCHES ====================
    
    def rechercher_par_id(self, id_livre):
        """
        Rechercher un livre par son ID
        """
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
        """
        Rechercher des livres par titre (recherche partielle)
        """
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
        """
        Rechercher des livres par auteur (recherche partielle)
        """
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
    
    def get_tous_les_livres_texte(self):
        """
        Retourne tous les livres sous forme de texte (pour le chatbot)
        """
        livres = self.afficher_tous_les_livres()
        if not livres:
            return "Aucun livre dans la bibliothèque."
        
        texte = "Voici tous les livres de la bibliothèque :\n\n"
        for livre in livres:
            texte += f"• ID {livre.id_livre} : {livre.titre} - {livre.auteur} ({livre.categorie}) - {livre.statut} ({livre.quantite_disponible} ex.)\n"
        return texte
    
    # ==================== DONNÉES DE TEST ====================
    
    def ajouter_donnees_test(self):
        """
        Ajoute des livres d'exemple (pour tester l'application)
        """
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