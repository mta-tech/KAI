import re
import os
from dotenv import load_dotenv
from app.utils.prompts.agent_prompts import NER_PROMPTS
import requests

load_dotenv()

def request_ner_service(query, labels: list[str], threshold=0.5):
    url = os.getenv("GLINER_API_BASE")
    url = url.rstrip("/") + "/get-ner-objects"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    data = {
        "query": query,
        "ner_category": labels,
        "threshold": threshold
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()
    
def get_ner_labels(text: str) -> list[str]:
    labels = [
        'company', 'year', 'month', 'date', 'location', 'country', 'city', 'status', 'category'
        ]
    return labels

def get_prompt_text_ner(text, labels_entities_ner):
    sorted_results = sorted(labels_entities_ner, key=lambda x: x['start'], reverse=True)
    
    for entity in sorted_results:
        start, end, label = entity['start'], entity['end'], entity['label'].upper()
        text = text[:start] + f"<{label}>" + text[end:]  # Replace text with label placeholder

    return text

def get_labels_entities(labels_entities_ner):
    unique_labels = set()
    unique_entities = set()

    for item in labels_entities_ner:
        unique_labels.add(item["label"])
        unique_entities.add(item["text"])

    return_dict = {
        "labels": list(unique_labels),
        "entities": list(unique_entities)
    }

    return return_dict

def generate_ner_llm(llm_model, prompt: str, existing_sql: str, new_prompt: str, ) -> str:
    prompt_query = NER_PROMPTS.format(
        prompt=prompt,
        new_prompt=new_prompt,
        existing_sql=existing_sql
    )

    response = llm_model.invoke(prompt_query)

    if isinstance(response.content, str):
        sql_response = re.sub(r"```(?:sql)?\n?", "", response.content).strip("`")
        return sql_response
    return None