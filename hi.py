from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = '8018410508:AAGRxxXKU8occ0xB-2nscmsS3OE2Y4APoYI'  # Replace with your bot's token

# Function to handle any incoming message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    print(f"User: {user.full_name} | Username: @{user.username} | Chat ID: {chat_id}")

    # Optional: reply to the user
    await update.message.reply_text(f"Hello {user.first_name}! Your chat ID is {chat_id}.")

# Function to start the bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send me any message and I'll tell you your chat ID.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
