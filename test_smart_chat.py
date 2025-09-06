import unittest
import os
import db
from telegram_handlers import start_smart_chat, handle_answer
from telegram import Update, Message, User, Chat
from unittest.mock import MagicMock, patch

class TestSmartChat(unittest.TestCase):
    def setUp(self):
        # Set up a mock update and context
        self.update = MagicMock(spec=Update)
        self.context = MagicMock()
        self.update.effective_chat = MagicMock(spec=Chat)
        self.update.effective_chat.id = 12345
        self.update.message = MagicMock(spec=Message)
        self.update.message.text = "Hello"
        self.update.message.from_user = MagicMock(spec=User)
        self.update.message.from_user.id = 12345

        # Initialize the database
        db.init_db()

    @patch('smart_chat.get_embeddings')
    @patch('smart_chat.FAISS')
    def test_smart_chat_session(self, mock_faiss, mock_get_embeddings):
        # 1. Start the smart chat session
        with patch('telegram_handlers.send_formatted_text') as mock_send:
            start_smart_chat(self.update, self.context)
            mock_send.assert_called_with(
                self.update, "Welcome to the Smart Chat! You can start chatting with the AI now."
            )

        # 2. Send a message
        with patch('smart_chat.run_chat') as mock_run_chat:
            mock_run_chat.return_value = "AI Response"
            handle_answer(self.update, self.context)
            # Check that the bot responded
            self.update.message.reply_text.assert_called_with("AI Response")

        # 3. Check the database
        conn = db.get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM smart_chat_history WHERE chat_id = ?", (12345,))
        rows = cur.fetchall()
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['role'], 'user')
        self.assertEqual(rows[0]['message'], 'Hello')
        self.assertEqual(rows[1]['role'], 'ai')
        conn.close()

    def tearDown(self):
        # Clean up the database
        os.remove("bot.db")

if __name__ == '__main__':
    unittest.main()
