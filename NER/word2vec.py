import json
from gensim.models import Word2Vec
import re 

file_path = './NER/NER_DATA/word2vec.txt'

def preprocess_text(text):
    return re.sub(r'\W+', ' ', text.lower()).split()

sentences = []  

with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        processed_line = preprocess_text(line)
        sentences.append(processed_line)

model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

model.save("word2vec.model")