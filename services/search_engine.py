import os, time, re
from services.file_handler import extract_text_from_file

def search_in_documents(keyword, documents_dir="storage/documents"):
    start_time = time.time()
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    results = []

    for filename in os.listdir(documents_dir):
        filepath = os.path.join(documents_dir, filename)
        if os.path.isfile(filepath):
            try:
                text = extract_text_from_file(filepath)
                matches = pattern.findall(text)
                if matches:
                    lines = [line.strip() for line in text.split('\n') if pattern.search(line)]
                    results.append({
                        "filename": filename,
                        "matches": lines
                    })
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    end_time = time.time()
    duration = round(end_time - start_time, 4)

    return results, duration
