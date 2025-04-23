import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
TOKEN = "7810952815:AAETk8FaU6rtq8_ICAJuwLGLJA8ZcMILrMM"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Psychology Test Bot. Type /help for available commands.")
    
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Available commands: /start, /help, /login")
    
def login(update: Update, context: CallbackContext) -> None:
    # This stub preserves your current terminal login, which runs separately.
    update.message.reply_text("Proceeding with terminal login. Please check your terminal.")
    # Optionally, you can integrate a call to your existing login logic if needed.

def message_handler(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text
    # Process the text with your psychology test logic (placeholder)
    response = f"Echo: {user_text}"
    update.message.reply_text(response)

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    # Start the Telegram bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
