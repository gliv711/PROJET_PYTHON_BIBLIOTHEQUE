# check_models.py
import google.generativeai as genai
from config import get_api_key

api_key = get_api_key()
genai.configure(api_key=api_key)

print("🔍 Modèles disponibles sur ton compte :\n")
print("="*60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Description: {model.description[:80] if model.description else 'N/A'}")
        print(f"   Max tokens: {model.input_token_limit}\n")

print("="*60)
print("💡 Copie le nom du modèle que tu veux utiliser")