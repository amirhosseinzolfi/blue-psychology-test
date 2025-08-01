import logging
# Fix the import statement by using the correct filename with hyphen
from psychology_test_ai import tele_initialize, tele_get_question, tele_process_answer, tele_summarize

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
TOKEN = "7810952815:AAETk8FaU6rtq8_ICAJuwLGLJA8ZcMILrMM"

# Global dictionary to hold test sessions by chat id
user_tests = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome to the Psychology Test Bot. Type /help for available commands.")

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Available commands: /start, /help, /login, /start_test")

def login(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Proceeding with terminal login. Please check your terminal.")

def start_test(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "User"
    # Initialize a new test session using the psychology test functions
    state = tele_initialize(user_name)
    user_tests[user_id] = state
    q_text = tele_get_question(state)
    update.message.reply_text(f"Hello {user_name}, your test is starting:\n\n{q_text}")

def test_message_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    if user_id in user_tests:
        state = user_tests[user_id]
        user_input = update.message.text
        result = tele_process_answer(state, user_input)
        # Send the acknowledgment message
        update.message.reply_text(result["ack"])
        # If there is a next question, send it; otherwise, summarize the test
        if result["next"]:
            update.message.reply_text(result["next"])
        else:
            summary = tele_summarize(state)
            update.message.reply_text(f"Test Completed!\n\nSummary:\n{summary}")
            # Optionally, remove finished test session
            user_tests.pop(user_id, None)
    else:
        # If no test session is active, ignore or prompt user with instructions
        update.message.reply_text("To start the test, type /start_test.")

def message_handler(update: Update, context: CallbackContext) -> None:
    # Default message handler for non-test messages
    user_id = update.effective_chat.id
    if user_id not in user_tests:
        user_text = update.message.text
        response = f"Echo: {user_text}"
        update.message.reply_text(response)
    # If there is an active test session, let test_message_handler handle user responses.

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("login", login))
    dispatcher.add_handler(CommandHandler("start_test", start_test))
    # Handler for test responses; it should be placed before the default message handler.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, test_message_handler))
    # Fallback message handler for non-test messages.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
