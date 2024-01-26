import json
from sklearn.feature_extraction.text import TfidfVectorizer

def sort_documents_by_tfidf(indices, documents):
    all_documents = ' '.join(documents)
    vectorizer = TfidfVectorizer()
    try: 
        tfidf_matrix = vectorizer.fit_transform([all_documents])
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = dict(zip(feature_names, tfidf_matrix.toarray()[0]))
        indices_map = {idx: documents.index(database[idx]['content']) for idx in indices}
        sorted_indices = sorted(indices, key=lambda idx: max(tfidf_scores.get(word, 0) for word in documents[indices_map[idx]].split()), reverse=True)
        return sorted_indices
    except Exception as e: 
        print("!!!!SKIPPED!!!!")
        return indices


def load_json_file(file_path):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def prepSortedDocs(database):
    tag_doc = {}
    for i in range(len(database)):
        print(i)
        item = database[i]
        for elem in item["tags"]:
            if elem not in tag_doc.keys(): tag_doc[elem] = []
            tag_doc[elem].append(i)
    
    print("tag_doc prepared")

    sorted_tags = {}
    x = 1
    for tag, indices in tag_doc.items():
        print(x)
        x += 1
        sorted_indices = sort_documents_by_tfidf(indices, [database[idx]['content'] for idx in indices])
        sorted_tags[tag] = sorted_indices
    
    return sorted_tags

file_path = 'db.json'
database = load_json_file(file_path)

sorted_tags = prepSortedDocs(database)

with open('tags_to_doc_indices.json', 'w') as json_file:
    json.dump(sorted_tags, json_file)