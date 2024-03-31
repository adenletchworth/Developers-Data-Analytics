import json
import re 

file_path = './NER/NER_DATA/word2vec.txt'
json_file_path = './NER/NER_DATA/word2vec.json'

def preprocess_text(text):
    return re.sub(r'\W+', ' ', text.lower()).split()

data = []

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        original_line = line.strip() 
        tokenized_line = preprocess_text(line)
        if original_line:  
            data.append({
                "original": original_line,
                "tokenized": tokenized_line
            })

with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
