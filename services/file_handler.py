import os
import fitz  # PyMuPDF
import docx
import docx2txt
from werkzeug.utils import secure_filename

# مسار التخزين المحلي
DOCUMENTS_DIR = "storage/documents"

# حفظ الملف في مجلد التخزين
def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)
    file.save(file_path)
    return file_path


# استخراج النص الكامل من PDF أو Word
def extract_text_from_file(file_path):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        return None


# استخراج أول سطر غير فارغ كعنوان
def extract_title_from_file(file_path):
    text = extract_text_from_file(file_path)
    if not text:
        return "No Title"
    for line in text.splitlines():
        clean_line = line.strip()
        if clean_line:
            return clean_line
    return "Untitled"


# استخراج النص من PDF باستخدام PyMuPDF
def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# استخراج النص من Word باستخدام python-docx
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# استخراج العنوان من كل ملف
def get_all_documents_with_titles(documents_dir):
    documents = []
    for filename in os.listdir(documents_dir):
        filepath = os.path.join(documents_dir, filename)
        if os.path.isfile(filepath):
            try:
                title = extract_title_from_file(filepath)
                documents.append({
                    'filename': filename,
                    'title': title
                })
            except Exception as e:
                print(f"Error extracting title from {filename}: {e}")
    # ترتيب أبجدي حسب العنوان
    documents.sort(key=lambda d: d['title'].lower())
    return documents

# تبحث في كل الملفات النصوص اللي تحتوي على الكلمات المفتاحية
def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    elif ext in [".docx", ".doc"]:
        # docx2txt تستخدم docx فقط لكن تقدر تحاول
        text = docx2txt.process(filepath)
        return text
    else:
        raise Exception("Unsupported file format")
# حساب حجم الملف
def get_storage_stats(directory):
    total_size = 0
    file_count = 0

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            file_count += 1
            total_size += os.path.getsize(filepath)

    # تحويل الحجم إلى ميجابايت مع تقريب رقمين عشريين
    size_mb = round(total_size / (1024 * 1024), 2)
    return file_count, size_mb