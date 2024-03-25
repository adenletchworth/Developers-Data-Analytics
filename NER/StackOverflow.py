import re
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import BigQuery as bq
from typing import Generator, Optional, Union, Dict, List
import json

nlp = spacy.load("en_core_web_sm")

def normalize_and_annotate_with_phrase_matcher_batched(batches: Generator[List[Union[tuple, Dict[str, any]]], None, None]):
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    titles_seen = set()

    for batch in batches:
        for title, body in batch:
            normalized_title = title.lower()
            if normalized_title not in titles_seen:
                pattern = nlp.make_doc(normalized_title)
                matcher.add("TECH_TERM", [pattern])
                titles_seen.add(normalized_title)
            
        annotated_batch = []
        for title, body in batch:
            normalized_title = title.lower()
            modified_body = normalized_title + ". " + body.lower()
            doc = nlp(modified_body)

            matches = matcher(doc)
            entities = []
            for match_id, start, end in matches:
                span = doc[start:end]
                entities.append((span.start_char, span.end_char, "TECH_TERM"))

            annotated_batch.append((modified_body, {"entities": entities}))
        
        yield annotated_batch
        
def save_annotated_data_as_json(annotated_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(annotated_data, f, ensure_ascii=False, indent=4)


def create_data_for_word2vec(batches):
    annotated_batch = []
    for batch in batches:
        for body in batch:
            annotated_batch.append(body)
    return annotated_batch
    
        
def create_json_for_spacy():
    query = """
    SELECT title, body FROM `stack_overflow.posts_tag_wiki_excerpt`
    WHERE title IS NOT NULL AND body IS NOT NULL
    """

    batch_size = 10000  
    batches = bq.query_bigquery_batched(query, batch_size=batch_size)

    all_annotated_data = []

    for annotated_batch in normalize_and_annotate_with_phrase_matcher_batched(batches):
        all_annotated_data.extend(annotated_batch) 

    file_path = "./NER/CS_ENTITIES.json"
    save_annotated_data_as_json(all_annotated_data, file_path)


def create_txt_for_word2vec(file_path):
    query = """
    SELECT title,body FROM `stack_overflow.posts_tag_wiki_excerpt`
    WHERE body IS NOT NULL
    """
    
    batch_size = 10000  
    batches = bq.query_bigquery_batched(query, batch_size=batch_size)

    all_annotated_data = create_data_for_word2vec(batches)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        for _, sentence in all_annotated_data:
            file.write(sentence + '\n')  


# create_txt_for_word2vec('./NER/NER_DATA/word2vec.txt')