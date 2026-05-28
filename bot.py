import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai

# 1. Récupération des variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialisation de l'API Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Utilisation du modèle Flash (ultra-rapide et gratuit)
    ai_model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Configuration de Flask (Pour que Render reste actif)
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot de musique avec Gemini est en ligne !"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 3. Fonctions du Bot Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salut ! Je suis ton bot de musique boosté à l'IA Gemini. 🎧\n"
        "Dis-moi ce que tu veux créer !"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    try:
        # Génération de la réponse avec Gemini
        response = ai_model.generate_content(user_text)
        reply = response.text
        await update.message.reply_text(reply)
        
    except Exception as e:
        print(f"Erreur Gemini : {e}")
        await update.message.reply_text("Désolé, j'ai eu un petit problème pour traiter ta demande avec Gemini. Réessaie !")

# 4. Lancement de l'application
def main():
    if not TELEGRAM_TOKEN:
        print("Erreur : Aucun TELEGRAM_TOKEN trouvé.")
        return

    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Démarrage du bot Telegram (Gemini)...")
    application.run_polling()

if __name__ == '__main__':
    main()