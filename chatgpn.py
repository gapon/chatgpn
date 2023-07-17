import logging
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import openai

BOT_ENV = os.getenv('BOT_ENV')
TOKEN = os.getenv('CHATGPN_TOKEN')

OPENAI_TOKEN = os.getenv('OPENAI_TOKEN')
openai.api_key = OPENAI_TOKEN

allowed_users = [1183558,]

if BOT_ENV == 'prod':
    APP_NAME = 'https://gapon.me/'
    PORT = int(os.environ.get('PORT', '8444'))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # Checking whether the user is authorized
    user = update.effective_user
    if user.id not in allowed_users:
        logger.info('Access Denied')
        return

    user = update.effective_user
    await update.message.reply_text(f'Hello {user.first_name}')

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Checking whether the user is authorized
    user = update.effective_user
    if user.id not in allowed_users:
        logger.info('Access Denied')
        return
    prompt = ' '.join(context.args)
    await update.message.reply_text(get_completion(prompt))


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat", chat))

    # Run the bot until the user presses Ctrl-C
    if BOT_ENV == 'prod':
        application.run_webhook(
            listen='0.0.0.0',
            port=5000,
            url_path=TOKEN,
            #secret_token='ASecretTokenIHaveChangedByNow',
            webhook_url='https://gapon.me/'+TOKEN,
            #cert='cert.pem'
        )
    else:
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()