import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    ContextTypes, MessageHandler, 
    filters, 
    ConversationHandler,
    )
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

new_chat_keyboard = [[ "New chat"]]
new_chat_markup = ReplyKeyboardMarkup(new_chat_keyboard, one_time_keyboard=True)

chat_keyboard = [["End chat",],[ "New chat"]]
chat_markup = ReplyKeyboardMarkup(chat_keyboard, one_time_keyboard=True)


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
    await update.message.reply_text(f'Hello {user.first_name}', reply_markup=new_chat_markup)


# START OF CONVERSATION

GPT_CHAT = 0

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Checking whether the user is authorized
    user = update.effective_user
    if user.id not in allowed_users:
        logger.info('Access Denied')
        return ConversationHandler.END

    messages = []
    context.user_data["messages"] = messages
    
    await update.message.reply_text('How can I help you?')

    return GPT_CHAT

async def gpt_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chat with GPT"""
    messages = context.user_data["messages"]

    user_message = update.message.text
    messages.append({"role": "user", "content": user_message})

    reply = get_completion_from_messages(messages)
    messages.append({'role':'assistant', 'content': reply})
    context.user_data["messages"] = messages

    await update.message.reply_text(reply, reply_markup=chat_markup)
    return GPT_CHAT

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    context.user_data["messages"].clear()

    await update.message.reply_text("Bye! I hope we can talk again some day.", reply_markup=new_chat_markup)
    return ConversationHandler.END

# END OF CONVERSATION

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = context.user_data["messages"]
    await update.message.reply_text(messages)

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("debug", debug))

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("chat", new_chat),
                      MessageHandler(filters.Regex("^(New chat)$"), new_chat)],
        states={
            GPT_CHAT: [
                MessageHandler(filters.Regex("^(End chat)$"), end),
                MessageHandler(filters.Regex("^(New chat)$"), new_chat),
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