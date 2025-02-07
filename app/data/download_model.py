# app/data/models/download_model.py
import os
import gc
import torch
from gliner import GLiNER

def check_and_download_model():
    MODEL_REPO = "urchade/gliner_medium-v2.1"
    MODEL_NAME = MODEL_REPO.split("/")[-1]
    CACHE_DIR = "app/data/models/"
    MODEL_PATH = os.path.join(CACHE_DIR, MODEL_NAME)

    try:
        try:
            GLiNER.from_pretrained(MODEL_PATH, local_files_only=True)
            print("Local file exists!")
        except:
            print(f"Downloading model {MODEL_NAME}...")
            GLiNER.from_pretrained(MODEL_REPO).save_pretrained(MODEL_PATH)

        print("Model loaded successfully!")    
        
        gc.collect()  # Free CPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Free GPU memory
        print("Clear memory usage")    
    except Exception as e:
        print(f"Error loading model: {e}")
        raise RuntimeError("Failed to load GLiNER model")
    
    return None

if __name__ == "__main__":
    check_and_download_model()