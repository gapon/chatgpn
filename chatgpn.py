import logging
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

allowed_users = [1183558,]

BOT_ENV = os.getenv('BOT_ENV')
TOKEN = os.getenv('CHATGPN_TOKEN')

print(TOKEN)

if BOT_ENV == 'prod':
    APP_NAME = 'https://gapon.me/'
    PORT = int(os.environ.get('PORT', '8444'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(f'Hello {user.first_name}')


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # Run the bot until the user presses Ctrl-C
    if BOT_ENV == 'prod':
        application.start_webhook(listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url = APP_NAME + TOKEN)
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()