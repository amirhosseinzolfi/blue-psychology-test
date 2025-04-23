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
    # Create a reply keyboard with two test command buttons.
    keyboard = [[ "/start_test_a", "/start_test_b" ]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text(
        "به ربات تست روانشناسی خوش آمدید.\nلطفاً یکی از تست‌های موجود را انتخاب کنید:", # Translated text
        reply_markup=reply_markup
    )

def help_command(update: Update, context: CallbackContext) -> None:
    # Keep commands in English for Telegram functionality, but describe in Persian.
    help_text = (
        "دستورات موجود:\n"
        "/start - نمایش پیام خوشامدگویی و انتخاب تست\n"
        "/help - نمایش این راهنما\n"
        "/login - ورود از طریق ترمینال\n"
        "/start_test_a - شروع تست نوع A\n"
        "/start_test_b - شروع تست نوع B"
    )
    update.message.reply_text(help_text) # Translated text

def login(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("در حال انجام ورود از طریق ترمینال. لطفاً ترمینال خود را بررسی کنید.") # Translated text

def start_test(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_chat.id
    user_name = update.effective_user.first
