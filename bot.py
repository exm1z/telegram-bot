from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from config import BOT_TOKEN, ADMIN_CHAT_ID

# Стани для заявки
ASK_NAME, ASK_PHONE = range(2)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Залишити заявку", callback_data='leave_request')],
        [InlineKeyboardButton("Отримати інформацію", callback_data='get_info')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Привіт! Оберіть дію:", reply_markup=reply_markup)

# Обробка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'leave_request':
        await query.message.reply_text("Введіть своє ім’я:")
        return ASK_NAME
    elif query.data == 'get_info':
        await query.message.reply_text(
            "ℹ️ Ми надаємо XYZ. Зв'яжіться з нами або залиште заявку.\n\n(тут можна надіслати файл)"
        )
        # Приклад відправлення файлу:
        # with open('info.pdf', 'rb') as f:
        #     await query.message.reply_document(document=InputFile(f))
        return ConversationHandler.END

# Запит імені
async def ask_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text("Тепер введіть номер телефону:")
    return ASK_PHONE

# Запит номера
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['phone'] = update.message.text
    name = context.user_data['name']
    phone = context.user_data['phone']

    msg = f"📩 Нова заявка:\n\n👤 Ім’я: {name}\n📞 Телефон: {phone}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg)

    await update.message.reply_text("✅ Дякуємо! Заявку надіслано.")
    return ConversationHandler.END

# Скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Скасовано.")
    return ConversationHandler.END

# Головна функція
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("✅ Бот запущено...")
    app.run_polling()

if __name__ == '__main__':
    main()