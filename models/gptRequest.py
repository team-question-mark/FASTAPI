import openai
from config.configkey import API_KEY_OPENAI## 주호꺼
from config.configkey import API_KEY_OPENAI_JAC ## 내꺼

openai.api_key = API_KEY_OPENAI


def extract_meaningful_words(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": text}
        ],
        max_tokens=100,
        temperature=0,
    )

    choices = response['choices'][0]['message']['content']
    tokens = choices.strip().split()
    meaningful_words = []

    for token in tokens:
        if token.startswith('\"'):
            continue
        elif token.endswith('\"'):
            token = token[:-1]
        meaningful_words.append(token)

    return meaningful_words
