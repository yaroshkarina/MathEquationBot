import os
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


# Дані користувачів
user_data = {}

# Клавіатура
main_keyboard = ReplyKeyboardMarkup(
    [["Нове завдання", "Завершити сеанс"], ["Статистика", "Налаштування"]],
    resize_keyboard=True
)


# ===== Допоміжні функції =====
def generate_task(level):
    if level == "легкий":
        a, b = random.randint(1, 20), random.randint(1, 20)
        op = random.choice(["+", "-"])
        question = f"{a} {op} {b}"
        answer = eval(question)
    elif level == "середній":
        op = random.choice(["*", "/"])
        if op == "*":
            a, b = random.randint(2, 12), random.randint(2, 12)
            answer = a * b
        else:
            b = random.randint(2, 12)
            answer = random.randint(2, 12)
            a = answer * b
        question = f"{a} {op} {b}"
    else:  # складний
        ops = ["+", "-", "*", "/"]
        b, c = random.randint(2, 12), random.randint(2, 12)
        op1, op2 = random.choice(ops), random.choice(ops)
        if op1 == "/":
            b = random.randint(2, 12)
            tmp = random.randint(2, 12)
            a = b * tmp
        else:
            a = random.randint(2, 12)
        expr = f"{a} {op1} {b} {op2} {c}"
        answer = int(eval(expr))
        question = expr
    return question, answer


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {
        "level": "легкий",
        "tasks": 0,
        "correct": 0,
        "wrong": 0,
        "active_task": None
    }
    await update.message.reply_text(
        "👋 Привіт! Це математичний бот.\n\n"
        "📚 Обери рівень складності в меню 'Налаштування', "
        "або почни з легкого рівня.\n\n"
        "➡️ Натисни 'Нове завдання', щоб розпочати!",
        reply_markup=main_keyboard
    )


async def new_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("Натисни /start для початку.")
        return

    level = user_data[user_id]["level"]
    question, answer = generate_task(level)
    user_data[user_id]["active_task"] = answer

    await update.message.reply_text(f"✏️ Розвʼяжи: {question} = ?", reply_markup=main_keyboard)


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data or user_data[user_id]["active_task"] is None:
        return

    try:
        user_answer = int(update.message.text)
        correct_answer = user_data[user_id]["active_task"]

        user_data[user_id]["tasks"] += 1
        if user_answer == correct_answer:
            user_data[user_id]["correct"] += 1
            await update.message.reply_text("✅ Правильно!", reply_markup=main_keyboard)
        else:
            user_data[user_id]["wrong"] += 1
            await update.message.reply_text(
                f"❌ Неправильно. Правильна відповідь: {correct_answer}",
                reply_markup=main_keyboard
            )
        user_data[user_id]["active_task"] = None
    except ValueError:
        pass


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["легкий", "середній", "складний"]]
    await update.message.reply_text(
        "⚙️ Обери рівень складності:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def set_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if text in ["легкий", "середній", "складний"]:
        user_data[user_id]["level"] = text
        await update.message.reply_text(
            f"✅ Рівень змінено на: {text}", reply_markup=main_keyboard
        )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = user_data.get(user_id)
    if not stats:
        await update.message.reply_text("Немає статистики. Натисни /start")
        return

    await update.message.reply_text(
        f"📊 Твоя статистика:\n"
        f"Рівень: {stats['level']}\n"
        f"Прикладів розвʼязано: {stats['tasks']}\n"
        f"Правильних: {stats['correct']}\n"
        f"Помилкових: {stats['wrong']}",
        reply_markup=main_keyboard
    )


async def end_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data:
        await update.message.reply_text(
            "✅ Сеанс завершено.\n\n"
            "Якщо захочеш продовжити пізніше — натисни кнопку 'Нове завдання'.",
            reply_markup=main_keyboard
        )
        user_data[user_id]["active_task"] = None


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Нове завдання$"), new_task))
    app.add_handler(MessageHandler(filters.Regex("^Статистика$"), stats))
    app.add_handler(MessageHandler(filters.Regex("^Налаштування$"), settings))
    app.add_handler(MessageHandler(filters.Regex("^Завершити сеанс$"), end_session))
    app.add_handler(MessageHandler(filters.TEXT, set_level))
    app.add_handler(MessageHandler(filters.TEXT, check_answer))

    app.run_polling()


if __name__ == "__main__":
    main()
