import os
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

# 1. Récupération des variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialisation du client OpenAI
ai_client = OpenAI(api_key=OPENAI_API_KEY)

# 2. Configuration de Flask (Pour éviter que Render ne coupe le Web Service)
app = Flask(__name__)

@app.route('/')
def home():
    return "Le bot de musique est en ligne et opérationnel !"

def run_flask():
    # Render attribue un port dynamiquement, on le récupère ici
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 3. Fonctions de gestion du Bot Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Message de bienvenue quand on tape /start"""
    await update.message.reply_text(
        "Salut ! Je suis ton bot de musique boosté à l'IA. 🎧\n"
        "Dis-moi ce que tu veux créer ou écris-moi un message !"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestion des messages textuels avec OpenAI"""
    user_text = update.message.text
    
    try:
        # Envoi de la requête à l'API OpenAI (Modèle GPT-3.5 ou GPT-4o-mini)
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_text}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
        
    except Exception as e:
        print(f"Erreur OpenAI : {e}")
        await update.message.reply_text("Désolé, j'ai eu un petit problème pour traiter ta demande avec l'IA. Réessaie !")

# 4. Lancement général de l'application
def main():
    if not TELEGRAM_TOKEN:
        print("Erreur : Aucun TELEGRAM_TOKEN trouvé dans l'environnement.")
        return

    # Création de l'application Telegram
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Liaison des commandes et des messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Lancement du serveur Flask dans un thread secondaire pour satisfaire le port Render
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Lancement du bot en mode écoute active (Polling)
    print("Démarrage du bot Telegram...")
    application.run_polling()

if __name__ == '__main__':
    main()