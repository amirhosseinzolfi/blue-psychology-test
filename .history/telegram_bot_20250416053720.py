import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# Import new functions from psychology-test
from psychology_test import tele_initialize, tele_get_question, tele_process_answer, tele_summarize

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram Bot Token
TOKEN = "7810952815:AAETk8FaU6rtq8_ICAJuwLGLJA8ZcMILrMM"

# Global dictionary to hold test sessions by chat id
user_tests = {}

def start(update: Update, context: CallbackContext) -> None:
    # Create a reply keyboard with two test command buttons with attractive emoji.
    keyboard = [[ "💡 تست mbti", "🎯 تست دیسک" ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "🌟 به ربات تست روانشناسی خوش آمدید!\n💬 لطفاً یکی از تست‌های زیر را انتخاب کنید:",  # updated greeting
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("📌 دستورات موجود: /start, /help, /login, /start_test")  # updated help message

def login(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("🔑 در حال ورود به ترمینال. لطفاً ترمینال خود را بررسی کنید.")  # updated login message

def start_test(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user_name = update.effective_user.first_name or "کاربر"  # updated default username
    test_type = None
    # Check if the message indicates a specific test type using attractive button text.
    if update.message.text == "💡 تست mbti":
        test_type = "A"
    elif update.message.text == "🎯 تست دیسک":
        test_type = "B"
    # Initialize a new test session; assume tele_initialize accepts an optional test type.
    state = tele_initialize(user_name, test_type) if test_type else tele_initialize(user_name)
    user_tests[user_id] = state
    q_text = tele_get_question(state)
    update.message.reply_text(f"👋 سلام {user_name}، تست شما شروع می‌شود:\n\n{q_text}")  # updated test start message

def test_message_handler(update: Update, context: CallbackContext) -> None:
    # If the user selects one of the test buttons and no test session is active, start the test.
    if update.message.text in ["💡 تست mbti", "🎯 تست دیسک"]:
        return start_test(update, context)
    user_id = update.effective_chat.id
    if user_id in user_tests:
        state = user_tests[user_id]
        user_input = update.message.text
        result = tele_process_answer(state, user_input)
        # Send the acknowledgment message with emoji.
        update.message.reply_text(f"✅ {result['ack']}")
        # If there is a next question, send it; otherwise, summarize the test.
        if result["next"]:
            update.message.reply_text(f"➡️ {result['next']}")
        else:
            summary = tele_summarize(state)
            update.message.reply_text(f"🏁 تست به پایان رسید!\n\n📋 خلاصه:\n{summary}")
            # Optionally, remove finished test session.
            user_tests.pop(user_id, None)
    else:
        # If no test session is active, prompt user with instructions.
        update.message.reply_text("❗️ برای شروع تست، لطفاً یکی از دکمه‌های ارائه شده را انتخاب کنید.")

def message_handler(update: Update, context: CallbackContext) -> None:
    # Default message handler for non-test messages
    user_id = update.effective_chat.id
    if user_id not in user_tests:
        user_text = update.message.text
        response = f"🔊 اکُو: {user_text}"  # updated echo message
        update.message.reply_text(response)
    # If there is an active test session, let test_message_handler handle user responses.

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("login", login))
    # Add new command handlers for specific test buttons.
    dispatcher.add_handler(CommandHandler("start_test_a", start_test))
    dispatcher.add_handler(CommandHandler("start_test_b", start_test))
    # Retain the generic test start command.
    dispatcher.add_handler(CommandHandler("start_test", start_test))
    # Handler for test responses; it should be placed before the default message handler.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, test_message_handler))
    # Fallback message handler for non-test messages.
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
