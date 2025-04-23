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
        test_type = "A" # Or perhaps "mbti" is better? Adjust as needed for psychology_test.py
    elif update.message.text == "🎯 تست دیسک":
        test_type = "B" # Or perhaps "disc" is better? Adjust as needed for psychology_test.py
    
    # Initialize the test state with only the user_name.
    state = tele_initialize(user_name)
    
    # Store the selected test type in the state object.
    # Note: psychology_test.py functions (tele_get_question, etc.) must be updated
    # to use state['test_type'] if they need to differentiate tests.
    if test_type:
        state['test_type'] = test_type 
        
    user_tests[user_id] = state
    q_text = tele_get_question(state) # tele_get_question needs to use state['test_type']
    update.message.reply_text(f"👋 سلام {user_name}، تست شما شروع می‌شود:\n\n{q_text}")  # updated test start message

def test_message_handler(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    if user_id in user_tests:
        state = user_tests[user_id]
        user_input = update.message.text
        result = tele_process_answer(state, user_input)
        # Send the acknowledgment message with emoji.
        update.message.reply_text(f"✅ {result['ack']}")
        # If there is a next question, send it; otherwise, summarize the test
        if result["next"]:
            update.message.reply_text(f"➡️ {result['next']}")
        else:
            summary = tele_summarize(state)
            update.message.reply_text(f"🏁 تست به پایان رسید!\n\n📋 خلاصه:\n{summary}")  # updated test completion message
            # Optionally, remove finished test session
            user_tests.pop(user_id, None)
    else:
        # If no test session is active, prompt user with instructions.
        update.message.reply_text("❗️ برای شروع تست، لطفاً یکی از دکمه‌های ارائه شده را انتخاب کنید.")  # updated instruction

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
    
    # Handler for specific test button texts - triggers start_test
    dispatcher.add_handler(MessageHandler(Filters.regex('^💡 تست mbti$'), start_test))
    dispatcher.add_handler(MessageHandler(Filters.regex('^🎯 تست دیسک$'), start_test))

    # Optional: Make /start_test show the buttons again if needed, or remove it
    # For now, let's make it call start() to show buttons
    dispatcher.add_handler(CommandHandler("start_test", start)) 

    # Handler for test answers (when a test is active)
    # This needs to be after the button handlers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, test_message_handler))
    
    # Fallback message handler for other non-command text (when no test is active)
    # This should be checked last or integrated into test_message_handler's else block
    # Let's keep the existing message_handler but ensure it's placed correctly
    # Note: The current test_message_handler already handles the 'else' case (no active test)
    # So, the separate message_handler might be redundant if test_message_handler covers all non-command text.
    # Let's remove the separate message_handler for simplicity.
    # dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler)) # Removed

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
