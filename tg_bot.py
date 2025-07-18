import logging
import os
import telegram

from environs import Env
from functools import partial
from telegram import Update
from telegram.ext import MessageHandler, Updater, CallbackContext, Filters

from bot_utils import get_response_dialogflow


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, admin_chat_id):
        super().__init__()
        self.bot = bot
        self.admin_chat_id = admin_chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=admin_chat_id, text=log_entry)


def handle_dialogflow_reply(update: Update, context: CallbackContext, project_id: str):
    chat_id = update.effective_chat.id
    session_id = f'tg_{chat_id}'

    context.bot.send_message(
        chat_id=chat_id,
        text=get_response_dialogflow(
            project_id,
            session_id,
            update.message.text
        ).query_result.fulfillment_text
    )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env.str('GOOGLE_APPLICATION_CREDENTIALS')

    tg_token = env.str('TG_TOKEN')
    admin_chat_id = env.int('ADMIN_CHAT_ID')
    project_id = env.str('DIALOG_FLOW_PROJECT_ID')
    bot = telegram.Bot(token=tg_token)

    log_handler = TelegramLogsHandler(bot, admin_chat_id)
    log_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '[telegram_bot] %(asctime)s - %(levelname)s - %(message)s'
    )
    log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(log_handler)

    updater = Updater(token=tg_token)
    dispatcher = updater.dispatcher

    dialogflow_handler = MessageHandler(
        Filters.text & ~Filters.command,
        partial(handle_dialogflow_reply, project_id=project_id)
    )
    dispatcher.add_handler(dialogflow_handler)

    updater.start_polling()
    updater.idle()
