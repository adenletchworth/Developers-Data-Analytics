import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer

class NamedEntityRecognizer:
    def __init__(self, model_path):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.model.eval()

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=-1)

        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        tags = [self.model.config.id2label[pred.item()] for pred in predictions[0]]

        entities = []
        current_entity = ""
        current_tag = None

        for token, tag in zip(tokens, tags):
            if token in ['[CLS]', '[SEP]']:
                continue

            if token.startswith("##"):
                current_entity += token[2:]
            else:
                if current_entity:
                    entities.append((current_entity, current_tag))
                current_entity = token
                current_tag = tag

        if current_entity:
            entities.append((current_entity, current_tag))

        filtered_entities = [entity for entity, tag in entities if tag != 'LABEL_27'] # LABEL_27 is the tag for 'O'

        return filtered_entities
    
# model_name = 'adenletchworth/CS-NER'
# ner = NamedEntityRecognizer(model_name)
# text = "example text with Python and other Named Entity Recognition (NER) related words. I need CS domain, Computer Science, Deep Learning, Machine Learning, and Natural Language Processing."
# print(ner.predict(text))

