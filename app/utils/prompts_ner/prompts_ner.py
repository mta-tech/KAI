from gliner import GLiNER
import re
import os
from dotenv import load_dotenv
# from collections import defaultdict
from app.utils.prompts.agent_prompts import NER_PROMPTS

import warnings
warnings.simplefilter("ignore")

load_dotenv()

def get_ner_labels(text: str) -> list[str]:
    labels = ['company', 'year', 'month', 'date', 'period']
    return labels

def get_ner(text: str, labels: list[str]) -> list[dict, str]:
    model_repo = os.getenv("GLINER_REPO")
    model_name = model_repo.split("/")[-1]
    model_path = os.path.join(os.getenv("GLINER_LOCAL_PATH"), model_name)

    model = GLiNER.from_pretrained(model_path)
    results = model.predict_entities(text, labels) or []

    return results

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

# def replace_entities_in_sql(cached_sql, cached_entities, new_entities):
#     MONTH_MAP = {
#         "january": 1, "february": 2, "march": 3, "april": 4,
#         "may": 5, "june": 6, "july": 7, "august": 8,
#         "september": 9, "october": 10, "november": 11, "december": 12
#     }
    
#     # Group new entities by label
#     new_entity_dict = defaultdict(list)
#     for entity in new_entities:
#         new_entity_dict[entity["label"]].append(entity["text"])

#     # Track used entities to avoid duplication issues
#     used_entities = defaultdict(int)

#     # Replace each entity value in SQL
#     for entity in cached_entities:
#         label, value = entity["label"], entity["text"]

#         if label in new_entity_dict:
#             # Get the next available replacement value
#             replacement_values = new_entity_dict[label]
#             if used_entities[label] < len(replacement_values):
#                 new_value = replacement_values[used_entities[label]]
#                 used_entities[label] += 1  # Move to next available replacement

#                 # Handle month names (convert to integer)
#                 if label == "month":
#                     new_value = str(MONTH_MAP.get(new_value.lower(), new_value))  # Convert month name to int if exists
#                     value = str(MONTH_MAP.get(value.lower(), value))


#                 # Replace only exact matches
#                 cached_sql = re.sub(rf"\b{re.escape(value)}\b", new_value, cached_sql, count=1)

#     return cached_sql