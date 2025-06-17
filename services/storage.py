import json
import os

CLASSIFICATION_FILE = "storage/classifications.json"

def load_classifications():
    if not os.path.exists(CLASSIFICATION_FILE):
        return {}
    with open(CLASSIFICATION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_classifications(data):
    with open(CLASSIFICATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
