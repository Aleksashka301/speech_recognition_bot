from environs import Env
from telegram import Update
from telegram.ext import MessageHandler, Updater, CallbackContext, CommandHandler, Filters


def start(update: Update, context: CallbackContext):
	context.bot.send_message(chat_id=update.effective_chat.id, text='Привет!')


def echo(update: Update, context: CallbackContext):
	context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


if __name__ == '__main__':
	env = Env()
	env.read_env()

	tg_token = env.str('TG_TOKEN')
	updater = Updater(token=tg_token)
	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(echo_handler)

	updater.start_polling()
