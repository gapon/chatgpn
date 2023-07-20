import logging
import os
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
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

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
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

async def chat2(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Checking whether the user is authorized
    user = update.effective_user
    if user.id not in allowed_users:
        logger.info('Access Denied')
        return
    prompt = ' '.join(context.args)
    await update.message.reply_text(get_completion(prompt))


'''Start of Chat'''
GPT_CHAT = 0

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Checking whether the user is authorized
    user = update.effective_user
    if user.id not in allowed_users:
        logger.info('Access Denied')
        return ConversationHandler.END

    """Starts the conversation and asks the user about their gender."""
    messages = []
    user_message = ' '.join(context.args)
    messages.append({"role": "user", "content": user_message})

    reply = get_completion_from_messages(messages)
    messages.append({'role':'assistant', 'content': reply})
    context.user_data["messages"] = messages
    await update.message.reply_text(reply)

    return GPT_CHAT

async def gpt_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    messages = context.user_data["messages"]

    user_message = update.message.text
    messages.append({"role": "user", "content": user_message})

    reply = get_completion_from_messages(messages)
    messages.append({'role':'assistant', 'content': reply})
    context.user_data["messages"] = messages

    await update.message.reply_text(reply)
    return GPT_CHAT

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Bye! I hope we can talk again some day.")

    return ConversationHandler.END

'''End of Chat'''

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("chat2", chat2))

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("chat", chat)],
        states={
            GPT_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gpt_chat),
                CommandHandler("end", end),
                ]
        },
        fallbacks=[CommandHandler("end", end)],
    )

    application.add_handler(conv_handler)

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