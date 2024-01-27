# Make all necessary imports
from docx import Document
import os
import nltk
import spacy
import json

nlp = spacy.load("en_core_web_sm")
nltk.download('punkt')

# Function to use nltk to split a paragraph into sentences
def split_into_sentences(text):
    sentences = nltk.sent_tokenize(text)
    return sentences

# Extract content from docs, split into sentences and put into a list of dictionaries.
def docWork(path):
    try: 
        doc = Document(path)
    except Exception as e: 
        print("!!!!!!SKIPPED!!!!!!")
        return []
    
    path_parts = path.split('\\')
    month = path_parts[-2]
    year = path_parts[-4]

    res = []
    for para in doc.paragraphs:
        if "***" in para.text: break
        content = para.text
        sentences = split_into_sentences(content)
        for sentence in sentences:
            res.append({"content": sentence, "tags": {}, "month": month, "year": year,})

    return res

# Extract entities from a given sentence
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

# Iterate through all the speeches and build database of content and tags
def speeches_iter():
    speeches_dir = "C:\\Users\\abhim\\OneDrive\\Documents\\Projects\\pib chatbot\\speeches"
    database = []
    x = 1
    for year in os.listdir(speeches_dir):
        year_file = os.path.join(speeches_dir, year, "English")
        for month in os.listdir(year_file):
            month_file = os.path.join(year_file, month)
            for filename in os.listdir(month_file):
                print(f"{x}. {filename}")
                path = os.path.join(month_file, filename)
                tempVec = docWork(path)
                database.extend(tempVec)
                x += 1

    x = 1
    for item in database:
        item["tags"] = entity_extraction(item["content"])
        print(x)
        x += 1

    return database

db = speeches_iter()

with open('db.json', 'w') as json_file:
    json.dump(db, json_file)