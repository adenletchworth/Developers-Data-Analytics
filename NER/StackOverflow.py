
import re
import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import NER.BigQuery as bq
from typing import Generator, Optional, Union, Dict, List
import json

nlp = spacy.load("en_core_web_sm")
matcher = PhraseMatcher(nlp.vocab, attr="LOWER")  

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



query = """
SELECT title, body FROM `stack_overflow.posts_tag_wiki_excerpt`
WHERE title IS NOT NULL AND body IS NOT NULL
"""

batches = bq.query_bigquery_batched(query, batch_size=500)
for i, annotated_batch in enumerate(normalize_and_annotate_with_phrase_matcher_batched(batches)):
    file_path = f"./NER_DATA/{i}.json"
    save_annotated_data_as_json(annotated_batch, file_path)
