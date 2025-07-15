import logging
import telegram
import os
import random
import vk_api

from environs import Env
from vk_api.longpoll import VkEventType, VkLongPoll

from bot_utils import get_response_dialogflow


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot, admin_chat_id):
        super().__init__()
        self.bot = bot
        self.admin_chat_id = admin_chat_id

    def emit(self, record):
        log_entry = self.format(record)
        self.bot.send_message(chat_id=admin_chat_id, text=log_entry)


def handle_dialogflow_reply(project_id, vk, event):
    user_id = event.user_id
    session_id = f'vk_{user_id}'
    response = get_response_dialogflow(project_id, session_id, event.text)

    if not response.query_result.intent.is_fallback:
        vk.messages.send(
            user_id=user_id,
            message=response.query_result.fulfillment_text,
            random_id=random.randint(1, 10000),
        )


if __name__ == '__main__':
    env = Env()
    env.read_env()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env.str('GOOGLE_APPLICATION_CREDENTIALS')

    vk_token = env.str('VK_TOKEN')
    tg_token = env.str('TG_TOKEN')
    admin_chat_id = env.int('ADMIN_CHAT_ID')
    project_id = env.str('DIALOG_FLOW_PROJECT_ID')

    bot = telegram.Bot(token=tg_token)

    log_handler = TelegramLogsHandler(bot, admin_chat_id)
    log_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(
        '[vk_bot] %(asctime)s - %(levelname)s - %(message)s'
    )
    log_handler.setFormatter(formatter)
    logging.getLogger().addHandler(log_handler)

    vk_session = vk_api.VkApi(token=vk_token)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                handle_dialogflow_reply(project_id, vk, event)
            except Exception:
                logging.exception('')
