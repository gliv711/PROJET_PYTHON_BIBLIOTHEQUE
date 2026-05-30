
import os
from dotenv import load_dotenv

load_dotenv()

# Clé API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DATABASE_NAME = "bibliotheque.db"

def get_api_key():
    """
    Retourne la clé API Gemini
    """
    if not GEMINI_API_KEY:
        raise ValueError("❌ Clé API non trouvée ! Vérifie ton fichier .env")
    return GEMINI_API_KEY

def get_db_path():
    """
    Retourne le chemin de la base de données
    """
    return DATABASE_NAME