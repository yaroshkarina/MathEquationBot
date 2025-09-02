import os
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters
from telegram.ext import CallbackContext
import logging

# Логування для дебагу
logging.basicConfig(level=logging.INFO)

# Токен
TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = Bot(token=TOKEN)

# Flask сервер
app = Flask(__name__)

# Dispatcher для обробки апдейтів
dispatcher = Dispatcher(bot, None, workers=0)

# ====== Хендлери команд ======
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привіт! Я бот для математики. Надішли мені приклад, і я допоможу 😉")

def echo(update: Update, context: CallbackContext):
    text = update.message.text
    try:
        result = eval(text)  # ⚠️ для прикладу, краще зробити без eval
        update.message.reply_text(f"Відповідь: {result}")
    except:
        update.message.reply_text("Не розумію цей приклад 😅")

# Додаємо хендлери
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

# ====== Flask endpoint ======
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Бот працює!"

if __name__ == "__main__":
    # Запускаємо Flask на порту, який дає Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
