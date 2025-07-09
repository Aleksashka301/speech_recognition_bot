import os
from environs import Env
from functools import partial
from google.cloud import dialogflow
from telegram import Update
from telegram.ext import MessageHandler, Updater, CallbackContext, CommandHandler, Filters


def start(update: Update, context: CallbackContext):
	context.bot.send_message(chat_id=update.effective_chat.id, text='Привет!')


def welcome_generation(update: Update, context: CallbackContext, project_id: str, language_code='ru'):
	session_client = dialogflow.SessionsClient()
	session = session_client.session_path(project_id, update.effective_chat.id)

	text_input = dialogflow.TextInput(text=update.message.text, language_code=language_code)
	query_input = dialogflow.QueryInput(text=text_input)

	response = session_client.detect_intent(
		request={'session': session, 'query_input': query_input}
	)

	context.bot.send_message(
		chat_id=update.effective_chat.id,
		text=response.query_result.fulfillment_text
	)


if __name__ == '__main__':
	env = Env()
	env.read_env()
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")

	tg_token = env.str('TG_TOKEN')
	project_id = env.str('DIALOG_FLOW_PROJECT_ID')

	updater = Updater(token=tg_token)
	dispatcher = updater.dispatcher

	start_handler = CommandHandler('start', start)
	welcome_generation_handler = MessageHandler(
		Filters.text & ~Filters.command,
		partial(welcome_generation, project_id=project_id)
	)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(welcome_generation_handler)

	updater.start_polling()
