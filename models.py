
class Livre:
    """
    Classe représentant un livre dans la bibliothèque.
    Correspond exactement aux champs demandés dans le cahier des charges.
    """
    
    def __init__(self, id_livre=None, titre="", auteur="", categorie="", 
                 annee_publication=2000, quantite_disponible=1, statut="disponible",
                 date_retour_prevue=None):
        """
        Constructeur d'un livre
        """
        self.id_livre = id_livre          # Identifiant unique auto-généré
        self.titre = titre                 # Titre du livre
        self.auteur = auteur               # Nom de l'auteur
        self.categorie = categorie         # Roman, Science, Histoire, Informatique...
        self.annee_publication = annee_publication  # Année de parution
        self.quantite_disponible = quantite_disponible  # Nombre d'exemplaires
        self.statut = statut               # disponible / emprunté / réservé
        self.date_retour_prevue = date_retour_prevue  # Pour les emprunts (bonus)
    
    def to_tuple(self):
        """
        Convertit le livre en tuple pour l'insertion SQL
        """
        return (self.titre, self.auteur, self.categorie, 
                self.annee_publication, self.quantite_disponible, 
                self.statut, self.date_retour_prevue)
    
    def afficher_court(self):
        """
        Retourne un résumé court du livre (pour l'affichage dans le chatbot)
        """
        return f"{self.titre} - {self.auteur} ({self.categorie}) - {self.statut} ({self.quantite_disponible} ex.)"
    
    def __str__(self):
        """
        Affichage complet d'un livre
        """
        retour = f"ID: {self.id_livre} | Titre: {self.titre} | Auteur: {self.auteur}\n"
        retour += f"Catégorie: {self.categorie} | Année: {self.annee_publication}\n"
        retour += f"Quantité: {self.quantite_disponible} | Statut: {self.statut}"
        if self.date_retour_prevue:
            retour += f" | Retour prévu: {self.date_retour_prevue}"
        return retour