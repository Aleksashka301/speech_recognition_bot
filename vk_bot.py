import os
import random
import vk_api

from environs import Env
from google.cloud import dialogflow
from vk_api.longpoll import VkEventType, VkLongPoll


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
	os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env.str('GOOGLE_APPLICATION_CREDENTIALS')

	vk_token = env.str('VK_TOKEN')
	project_id = env.str('DIALOG_FLOW_PROJECT_ID')

	vk_session = vk_api.VkApi(token=vk_token)
	vk = vk_session.get_api()
	longpoll = VkLongPoll(vk_session)

	for event in longpoll.listen():
		if event.type == VkEventType.MESSAGE_NEW and event.to_me:
			vk.messages.send(
				user_id=event.user_id,
				message=welcome(project_id, event.user_id, event.text),
				random_id=random.randint(1, 10000),
			)
