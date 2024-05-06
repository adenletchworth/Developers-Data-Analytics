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

        full_tokens = []
        current_token = ""
        for token, tag in zip(tokens, tags):
            if token.startswith("##"):
                current_token += token[2:] 
            else:
                if current_token:  
                    full_tokens.append((current_token, prev_tag))
                current_token = token  
                prev_tag = tag
                
        if current_token:
            full_tokens.append((current_token, prev_tag))

        return [token for token, tag in full_tokens if tag != 'O']