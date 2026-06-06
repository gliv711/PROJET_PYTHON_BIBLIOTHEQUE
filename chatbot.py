# chatbot.py
# Chatbot IA avec Google Gemini (nouvelle bibliothèque)

from google import genai
from google.genai import types
from config import get_api_key
from database import BibliothequeDB
import re

class ChatbotIntelligent:
    def __init__(self, db=None):
        # Connexion à la base de données
        if db is None:
            self.db = BibliothequeDB()
        else:
            self.db = db
            
        self.historique = []
        self.gemini_available = False
        
        try:
            api_key = get_api_key()
            if not api_key:
                print("⚠️ Aucune clé API trouvée dans .env")
                return
            
            # Nouvelle bibliothèque google.genai
            self.client = genai.Client(api_key=api_key)
            
            # Tester la connexion
            test_response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents="Test"
            )
            
            if test_response and test_response.text:
                self.gemini_available = True
                print("✅ Gemini API activée avec google.genai")
            else:
                print("❌ Le modèle n'a pas répondu correctement")
                
        except Exception as e:
            print(f"❌ Gemini non disponible: {e}")
            print("💡 Utilisation du mode secours")
    
    def get_contexte_bibliotheque(self):
        """Retourne tous les livres formatés pour le contexte"""
        livres = self.db.afficher_tous_les_livres()
        if not livres:
            return "La bibliothèque est actuellement vide."
        
        contexte = "=== LISTE COMPLÈTE DES LIVRES ===\n"
        for livre in livres:
            contexte += f"ID: {livre.id_livre} | "
            contexte += f"Titre: {livre.titre} | "
            contexte += f"Auteur: {livre.auteur} | "
            contexte += f"Catégorie: {livre.categorie} | "
            contexte += f"Année: {livre.annee_publication} | "
            contexte += f"Quantité: {livre.quantite_disponible} | "
            contexte += f"Statut: {livre.statut}"
            if livre.date_retour_prevue:
                contexte += f" | Retour prévu: {livre.date_retour_prevue}"
            contexte += "\n"
        
        total = len(livres)
        dispo = len([l for l in livres if l.statut == "disponible"])
        contexte += f"\n=== STATISTIQUES ===\n"
        contexte += f"Total des livres: {total}\n"
        contexte += f"Livres disponibles: {dispo}\n"
        
        return contexte
    
    def get_reponse(self, message):
        """100% Gemini"""
        
        if not self.gemini_available:
            return self.get_reponse_secours(message)
        
        self.historique.append(f"Utilisateur: {message}")
        if len(self.historique) > 10:
            self.historique = self.historique[-10:]
        
        contexte = self.get_contexte_bibliotheque()
        
        prompt = f"""Tu es un assistant de bibliothèque amical.

=== LIVRES ===
{contexte}

=== QUESTION ===
{message}

RÈGLES:
- Réponds UNIQUEMENT avec les livres listés
- Sois chaleureux, utilise des émojis
- Réponds en français, concis (max 80 mots)

RÉPONSE:"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            reponse = response.text.strip()
            if reponse:
                return reponse
            else:
                return self.get_reponse_secours(message)
        except Exception as e:
            print(f"Erreur: {e}")
            return self.get_reponse_secours(message)
    
    def get_reponse_secours(self, message):
        """Mode secours"""
        m = message.lower().strip()
        livres = self.db.afficher_tous_les_livres()
        
        if any(word in m for word in ["bonjour", "salut", "hello"]):
            return "👋 Bonjour ! Je suis votre assistant bibliothèque."
        
        if any(word in m for word in ["ça va", "comment vas"]):
            return "🤖 Ça va très bien ! Et vous ?"
        
        if any(word in m for word in ["merci"]):
            return "😊 Avec plaisir !"
        
        if any(word in m for word in ["au revoir", "bye"]):
            return "👋 Au revoir !"
        
        if any(word in m for word in ["disponible", "catalogue"]):
            dispo = [l for l in livres if l.statut == "disponible"]
            if dispo:
                r = "📚 Livres disponibles:\n"
                for l in dispo[:10]:
                    r += f"✅ {l.titre} - {l.auteur}\n"
                return r
            return "❌ Aucun livre disponible."
        
        if "id" in m:
            nums = re.findall(r'\d+', m)
            for n in nums:
                l = self.db.rechercher_par_id(int(n))
                if l:
                    return f"✅ ID {n}: {l.titre} - {l.auteur} ({l.statut})"
        
        for l in livres:
            if l.auteur.lower() in m:
                return f"📚 {l.auteur}: " + ", ".join([x.titre for x in self.db.rechercher_par_auteur(l.auteur)])
            if l.titre.lower() in m:
                return f"📖 {l.titre} - {l.auteur} ({l.statut})"
        
        return "🤖 Je n'ai pas compris. Tapez 'livres disponibles' pour voir le catalogue."