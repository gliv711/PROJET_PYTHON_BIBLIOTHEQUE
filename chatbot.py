# chatbot.py
# Chatbot IA avec Google Gemini - Version mise à jour (2025)

import google.generativeai as genai
from config import get_api_key
from database import BibliothequeDB

class ChatbotBibliotheque:
    """
    Chatbot intelligent qui utilise l'API Gemini pour répondre aux questions
    sur les livres de la bibliothèque.
    """
    
    def __init__(self):
        """Initialise le chatbot avec la clé API et la base de données"""
        # Configuration de l'API Gemini
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        # Utiliser le modèle disponible (gemini-pro)
        # Note: Sur la version gratuite, utilisez 'gemini-pro'
        try:
            self.model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            print(f"⚠️ Erreur avec gemini-pro, tentative avec gemini-1.5-pro...")
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except:
                self.model = genai.GenerativeModel('models/gemini-pro')
        
        # Connexion à la base de données
        self.db = BibliothequeDB()
        
        print("🤖 Chatbot IA initialisé avec succès !")
        print(f"📌 Modèle utilisé : {self.model.model_name}")
    
    def get_contexte_bibliotheque(self):
        """
        Récupère toutes les informations de la bibliothèque pour les donner à l'IA
        C'est ce qui permet au chatbot de répondre avec des données RÉELLES
        """
        livres = self.db.afficher_tous_les_livres()
        
        if not livres:
            return "La bibliothèque est vide pour le moment."
        
        contexte = "Voici la liste complète des livres dans notre bibliothèque :\n\n"
        
        for livre in livres:
            contexte += f"ID: {livre.id_livre} | "
            contexte += f"Titre: {livre.titre} | "
            contexte += f"Auteur: {livre.auteur} | "
            contexte += f"Catégorie: {livre.categorie} | "
            contexte += f"Année: {livre.annee_publication} | "
            contexte += f"Quantité disponible: {livre.quantite_disponible} | "
            contexte += f"Statut: {livre.statut}"
            
            if livre.date_retour_prevue:
                contexte += f" | Retour prévu: {livre.date_retour_prevue}"
            
            contexte += "\n"
        
        return contexte
    
    def poser_question(self, question_utilisateur):
        """
        Pose une question au chatbot et reçoit une réponse intelligente
        basée sur les données RÉELLES de la bibliothèque
        """
        # 1. Récupérer le contexte (tous les livres)
        contexte_biblio = self.get_contexte_bibliotheque()
        
        # 2. Construire le prompt complet (instructions + données + question)
        prompt = f"""
        Tu es un assistant IA spécialisé dans la gestion d'une bibliothèque.
        
        RÈGLES IMPORTANTES À RESPECTER ABSOLUMENT :
        1. Tu dois UNIQUEMENT répondre en utilisant les données de la bibliothèque fournies ci-dessous.
        2. Si la question ne concerne pas la bibliothèque, dis poliment que tu ne peux pas répondre.
        3. Si l'information n'est pas dans les données, dis honnêtement que tu ne sais pas.
        4. Réponds en français, de manière naturelle et amicale.
        5. Quand tu donnes des livres, liste-les avec leurs ID, titres, auteurs, statuts et disponibilités.
        6. Pour les recommandations, base-toi sur les catégories et les disponibilités.
        
        {contexte_biblio}
        
        Question de l'utilisateur : {question_utilisateur}
        
        Réponse (en français, naturel, avec les vraies données) :
        """
        
        try:
            # 3. Envoyer à Gemini
            reponse = self.model.generate_content(prompt)
            
            # 4. Retourner la réponse
            return reponse.text
        
        except Exception as e:
            # Si erreur, afficher un message utile
            if "quota" in str(e).lower():
                return "⚠️ Désolé, le quota API est atteint pour aujourd'hui. Réessaie demain ou vérifie ta clé API."
            elif "not found" in str(e).lower():
                return "⚠️ Problème de modèle API. Installation d'une solution alternative...\n" + \
                       "💡 En attendant, voici la recherche directe dans la base de données :\n\n" + \
                       self._reponse_sans_ia(question_utilisateur)
            else:
                return f"❌ Désolé, une erreur est survenue : {str(e)[:200]}"
    
    def _reponse_sans_ia(self, question):
        """
        Solution de secours : réponses basées sur des mots-clés (sans IA)
        Utilisé uniquement si l'API Gemini ne fonctionne pas
        """
        question_lower = question.lower()
        
        # Recherche par ID
        if "id" in question_lower:
            import re
            ids = re.findall(r'\d+', question)
            if ids:
                livre = self.db.rechercher_par_id(int(ids[0]))
                if livre:
                    return f"Oui, le livre avec l'ID {ids[0]} existe dans la bibliothèque.\n📖 {livre.afficher_court()}"
                else:
                    return f"Non, aucun livre avec l'ID {ids[0]} n'existe dans la bibliothèque."
        
        # Recherche par titre
        for livre in self.db.afficher_tous_les_livres():
            if livre.titre.lower() in question_lower:
                if "disponible" in question_lower:
                    if livre.statut == "disponible":
                        return f"Oui, '{livre.titre}' est disponible ! ({livre.quantite_disponible} exemplaire(s))"
                    else:
                        retour = f"Non, '{livre.titre}' est actuellement {livre.statut}."
                        if livre.date_retour_prevue:
                            retour += f" Retour prévu le : {livre.date_retour_prevue}"
                        return retour
                else:
                    return f"📖 {livre.afficher_court()}"
        
        # Recherche par auteur
        for livre in self.db.afficher_tous_les_livres():
            if livre.auteur.lower() in question_lower:
                return f"Voici les œuvres de {livre.auteur} :\n📖 {livre.afficher_court()}"
        
        # Recommandations
        if "recommand" in question_lower or "romantique" in question_lower:
            romans = [l for l in self.db.afficher_tous_les_livres() 
                     if "romantique" in l.categorie.lower() and l.statut == "disponible"]
            if romans:
                rep = "Voici mes recommandations de romans romantiques disponibles :\n"
                for l in romans:
                    rep += f"   📖 {l.titre} – {l.auteur} (Disponible)\n"
                return rep
        
        return "Je suis désolé, je n'ai pas compris ta question. Peux-tu reformuler ? (ex: 'ID 2 existe ?', 'Les Misérables disponible ?', 'livre de Victor Hugo')"
    
    def repondre_a_question_simple(self, question_utilisateur):
        """
        Version simplifiée pour les questions spécifiques
        """
        return self.poser_question(question_utilisateur)


# ==================== TEST DU CHATBOT ====================

def test_chatbot():
    """
    Fonction de test pour vérifier que le chatbot fonctionne
    """
    print("\n" + "="*60)
    print("🤖 TEST DU CHATBOT IA AVEC GEMINI")
    print("="*60 + "\n")
    
    # Créer le chatbot
    chatbot = ChatbotBibliotheque()
    
    # Questions de test (conformes aux exemples du cahier des charges)
    questions_test = [
        "Est-ce que le livre avec l'ID 2 existe ?",
        "Le roman Les Misérables est-il disponible ?",
        "Je veux un roman romantique facile à lire",
        "Je cherche un livre de Victor Hugo",
        "Quels livres sont disponibles actuellement ?",
        "Donne-moi tous les livres de la catégorie Informatique"
    ]
    
    for question in questions_test:
        print("\n" + "="*60)
        print(f"👤 QUESTION : {question}")
        print("-"*60)
        
        reponse = chatbot.poser_question(question)
        print(f"🤖 RÉPONSE :\n{reponse}")
        print("-"*60)
    
    print("\n✅ Test du chatbot terminé !")


if __name__ == "__main__":
    test_chatbot()