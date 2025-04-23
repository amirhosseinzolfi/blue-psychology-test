import logging
from telegram import Update, ReplyKeyboardMarkup # Keep ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Import necessary functions from psychology_test
from psychology_test import tele_initialize, tele_get_question, tele_process_answer, tele_summarize, get_available_tests # Added get_available_tests

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
TOKEN = "7810952815:AAETk8FaU6rtq8_ICAJuwLGLJA8ZcMILrMM"

# Global dictionary to hold test sessions by chat id
user_tests = {}

def start(update: Update, context: CallbackContext) -> None:
    """Sends a welcome message and dynamically generated test selection buttons."""
    available_tests = get_available_tests()
    if not available_tests:
        update.message.reply_text("Welcome! Unfortunately, no tests are available at the moment.")
        return

    # Create buttons dynamically based on available tests
    keyboard = []
    for test_info in available_tests:
        # Command format: /test_{index}
        button_text = f"/test_{test_info['index']} {test_info['name']}" 
        keyboard.append([button_text]) # Each test on its own row

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "Welcome to the Psychology Test Bot.\nPlease choose one of the available tests below:",
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Available commands:\n"
                              "/start - Show available tests\n"
                              "/help - Show this help message\n"
                              "/login - (Placeholder) Proceed with terminal login\n"
                              "Select a test using the buttons shown after /start.")

def login(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Proceeding with terminal login. Please check your terminal.")

def start_test(update: Update, context: CallbackContext) -> None:
    """Starts the test selected by the user via command."""
    user_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "User"
    
    # Extract test index from the command (e.g., /test_0)
    command_parts = update.message.text.split('_')
    test_index = 0 # Default to the first test
    if len(command_parts) == 2 and command_parts[0] == '/test' and command_parts[1].isdigit():
        test_index = int(command_parts[1])
        # Basic validation against available tests (optional but good practice)
        available_tests = get_available_tests()
        if not (0 <= test_index < len(available_tests)):
             update.message.reply_text(f"Invalid test selection. Please use /start to see available tests.")
             return # Stop processing if index is out of bounds
    else:
        # Handle generic /start_test or malformed command if needed, maybe redirect to /start
        update.message.reply_text("Please select a test using the buttons provided after typing /start.")
        return

    # Initialize the specific test using the index
    state = tele_initialize(user_name, test_index=test_index)
    user_tests[user_id] = state
    q_text = tele_get_question(state)
    if q_text:
        update.message.reply_text(f"Hello {user_name}, your selected test is starting:\n\n{q_text}")
    else:
        # Handle case where test initialization might fail or have no questions
        update.message.reply_text("Sorry, there was an issue starting the selected test.")
        user_tests.pop(user_id, None) # Clean up state

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
    
    # Use a single handler for all /test_{index} commands
    # The Filters.regex ensures this handler catches commands like /test_0, /test_1, etc.
    dispatcher.add_handler(CommandHandler(command=None, filters=Filters.regex(r'^/test_\d+'), callback=start_test))

    # Handler for test responses; placed before the default message handler.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, test_message_handler))
    # Fallback message handler for non-test messages.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
