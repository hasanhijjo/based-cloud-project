import os
import time
from services.file_handler import extract_text_from_file

# Example simple classification tree
classification_tree = {
    "finance": ["invoice", "bank", "payment", "budget"],
    "legal": ["contract", "agreement", "law", "policy"],
    "education": ["university", "course", "student", "research"],
    "technology": ["cloud", "software", "data", "AI", "system"],
    "health": ["medical", "patient", "treatment", "doctor"]
}

def classify_documents(documents_dir="storage/documents"):
    start_time = time.time()
    classifications = {}

    for category in classification_tree:
        classifications[category] = []

    for filename in os.listdir(documents_dir):
        filepath = os.path.join(documents_dir, filename)
        if os.path.isfile(filepath):
            try:
                text = extract_text_from_file(filepath).lower()
                for category, keywords in classification_tree.items():
                    if any(keyword in text for keyword in keywords):
                        classifications[category].append(filename)
                        break  # Stop at first match
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    end_time = time.time()
    duration = round(end_time - start_time, 4)

    return classifications, duration
