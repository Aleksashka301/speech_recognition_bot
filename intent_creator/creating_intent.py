import json
import os

from environs import Env
from google.cloud import dialogflow
from pathlib import Path


def create_intent(project_id, display_name, training_phrases_parts, message_texts):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)
    training_phrases = []

    for training_phrases_part in training_phrases_parts:
        part = dialogflow.Intent.TrainingPhrase.Part(text=training_phrases_part)
        training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
        training_phrases.append(training_phrase)

    text = dialogflow.Intent.Message.Text(text=message_texts)
    message = dialogflow.Intent.Message(text=text)

    intent = dialogflow.Intent(
        display_name=display_name,
        training_phrases=training_phrases,
        messages=[message],
    )

    response = intents_client.create_intent(
        request={'parent': parent, 'intent': intent}
    )

    return 'Intent created: {}'.format(response)


if __name__ == '__main__':
    env = Env()
    env.read_env(Path(__file__).resolve().parent.parent / '.env')

    project_id = env.str('DIALOG_FLOW_PROJECT_ID')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = env.str('GOOGLE_APPLICATION_CREDENTIALS')

    with open('intent_creator/questions.json', 'r', encoding='utf-8') as file:
        questions_file = file.read()

    message_texts = []
    training_phrases = json.loads(questions_file)['Устройство на работу']['questions']
    message_texts.append(json.loads(questions_file)['Устройство на работу']['answer'])

    intent = create_intent(
        project_id,
        'Getting a job',
        training_phrases,
        message_texts,
    )
    print(intent)
