import os
import vk_api

from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkEventType, VkLongPoll
from vk_api.utils import get_random_id


def welcome(project_id, session_id, text, language_code='ru'):
	session_client = dialogflow.SessionsClient()
	session = session_client.session_path(project_id, session_id)

	text_input = dialogflow.TextInput(text=text, language_code=language_code)
	query_input = dialogflow.QueryInput(text=text_input)

	response = session_client.detect_intent(request={'session': session, 'query_input': query_input})

	return response.query_result.fulfillment_text


if __name__ == '__main__':
	env = Env()
	env.read_env()
	os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = env.str("GOOGLE_APPLICATION_CREDENTIALS")

	vk_token = env.str('VK_TOKEN')
	project_id = env.str('DIALOG_FLOW_PROJECT_ID')

	vk_session = vk_api.VkApi(token=vk_token)
	vk = vk_session.get_api()
	longpoll = VkLongPoll(vk_session)

	for event in longpoll.listen():
		if event.type == VkEventType.MESSAGE_NEW:
			print('Новое сообщение')
			if event.to_me:
				print(f'Для меня от {event.user_id}')
				print(f'Текст сообщения: {event.text}')
				bot_response = welcome(project_id, event.user_id, event.text)

				vk.messages.send(
					user_id=event.user_id,
					message=bot_response,
					random_id=get_random_id(),
				)
				print(f'Сообщение от мея: {bot_response}')
