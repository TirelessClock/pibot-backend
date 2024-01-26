from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import json
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, resources={r"/interaction": {"origins": "https://pm-bot.vercel.app"}})

def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

database = load_json_file("db.json")
sorted_tags = load_json_file("tags_to_doc_indices.json")
nlp = spacy.load("en_core_web_sm")

key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=key,)

def chatGPTinteraction(prompt):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    res = ""
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            res += chunk.choices[0].delta.content

    return res

def entity_extraction(text):
    doc = nlp(text)
    labels_to_remove = ["CARDINAL", "PERCENT", "ORDINAL", "DATE", "QUANTITY", "TIME"]
    entities = []
    for ent in doc.ents:
        label = ent.label_
        if label not in labels_to_remove:
            entities.append(ent.text)

    entities = list(set(entities))

    return entities

def pick_docs(entities, st, k):
    res = {}
    for ent in entities:
        if ("modi" in ent.lower()) or ("prime minister" in ent.lower()) or ("pm" in ent.lower()) or ("narendra" in ent.lower()):
            continue
        if ent in st:
            indices = st[ent][:k]
            res[ent] = indices
    return res

def promptEngineering(prompt, entities):

    if len(entities) == 0:
        return "Say 'Sorry, I can't answer this question based on the Prime Minister's past speeches. May I help you with something else?'"

    text = "PM said in his speech:\n"
    for tag, _ in entities.items():
        text += f"{tag}: "
        for idx in entities[tag]:
            text += f"{database[idx]['content']}, "
        text += '\n'

    text += f"{prompt}. Respond briefly."

    return text

def inputPrompt(prompt):
    entities = entity_extraction(prompt)

    k = 5
    doc_idx = pick_docs(entities, sorted_tags, k)

    return chatGPTinteraction(promptEngineering(prompt, doc_idx))

@app.route('/interaction', methods=['POST'])
def chat_gpt_interaction():
    data = request.get_json()
    prompt = data['prompt']
    print(prompt)
    result = inputPrompt(prompt)
    return jsonify({'result': result})

# Add more routes as needed
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)