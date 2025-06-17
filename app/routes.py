import os, re , time
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, render_template, url_for, redirect,flash
from services.file_handler import save_file, extract_title_from_file, get_all_documents_with_titles, extract_text_from_file,get_storage_stats
from services.search_engine import search_in_documents
from services.storage import load_classifications, save_classifications
from services.classifier import classify_documents



app = Flask(__name__)
app.secret_key = 'your_super_secret_key_123'


@app.route("/")
def home():
    return render_template("home.html")

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    error = None
    success = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = "لم يتم اختيار ملف للرفع."
        else:
            file = request.files['file']
            if file.filename == '':
                error = "لم يتم اختيار ملف للرفع."
            elif not allowed_file(file.filename):
                error = "نوع الملف غير مدعوم. الرجاء رفع ملفات PDF أو DOCX فقط."
            else:
                filename = secure_filename(file.filename)
                file.save(os.path.join('storage/documents', filename))
                success = f"تم رفع الملف '{filename}' بنجاح."

    return render_template('upload.html', error=error, success=success)

@app.route("/api/search", methods=["GET"])
def api_search_documents():
    keyword = request.args.get("q")
    if not keyword:
        return jsonify({"error": "No search keyword provided"}), 400

    results = search_in_documents(keyword)

    return jsonify({
        "keyword": keyword,
        "results": results
    })

@app.route("/documents")
def list_documents():
    documents_dir = "storage/documents"
    documents = get_all_documents_with_titles(documents_dir)
    return render_template("documents.html", documents=documents)


@app.route("/search", methods=["GET", "POST"])
def search_documents():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form.get("keyword", "").strip()
        if keyword:
            documents_dir = "storage/documents"
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)

            for filename in os.listdir(documents_dir):
                filepath = os.path.join(documents_dir, filename)
                if os.path.isfile(filepath):
                    try:
                        # افتح الملف واستخدم extract_text من الخدمات (عندك دالة استخراج النص)
                        text = extract_text_from_file(filepath)  # لازم تكتبها أو تستخدم موجودة
                        matches = pattern.findall(text)
                        if matches:
                            # احصل على جمل أو سطور تحتوي النص
                            lines = [line.strip() for line in text.split('\n') if pattern.search(line)]
                            results.append({
                                "filename": filename,
                                "matches": lines
                            })
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
    return render_template("search.html", results=results, keyword=keyword)

@app.route("/classifications")
def show_classifications():
    documents_dir = "storage/documents"
    classifications = load_classifications()
    files = []

    for filename in os.listdir(documents_dir):
        filepath = os.path.join(documents_dir, filename)
        if os.path.isfile(filepath):
            category = classifications.get(filename, "Unclassified")
            files.append({"filename": filename, "category": category})

    return render_template("classifications.html", files=files)

@app.route("/classifications/update", methods=["POST"])
def update_classifications():
    documents_dir = "storage/documents"
    classifications = load_classifications()

    for filename in os.listdir(documents_dir):
        filepath = os.path.join(documents_dir, filename)
        if os.path.isfile(filepath):
            category = classify_documents(filepath)
            classifications[filename] = category

    save_classifications(classifications)
    return {"message": "Classifications updated successfully"}

from services.search_engine import search_in_documents
from services.classifier import classify_documents

@app.route("/stats")
def stats():
    documents_dir = "storage/documents"

    # فرز
    start_sort = time.time()
    # ممكن تنفذ الفرز هنا إن أردت
    end_sort = time.time()
    sort_time = round(end_sort - start_sort, 4)

    # بحث وهمي بكلمة "test" لحساب الوقت
    _, search_time = search_in_documents("test", documents_dir)

    # تصنيف وهمي
    _, classify_time = classify_documents(documents_dir)

    file_count, size_mb = get_storage_stats(documents_dir)

    return render_template("stats.html",
                           file_count=file_count,
                           size_mb=size_mb,
                           sort_time=sort_time,
                           search_time=search_time,
                           classify_time=classify_time)


@app.route("/categories")
def show_categories():
    classifications, classify_time = classify_documents()
    return render_template("categories.html", classifications=classifications, classify_time=classify_time)



UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'storage', 'documents')  # عدّل حسب مسار ملفاتك

@app.route('/delete_file', methods=['POST'])
def delete_file():
    filename = request.form.get('filename')
    if not filename:
        flash('لم يتم تحديد الملف للحذف.', 'error')
        return redirect(request.referrer or url_for('show_classifications'))

    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'تم حذف الملف {filename} بنجاح.', 'success')
        else:
            flash('الملف غير موجود.', 'error')
    except Exception as e:
        flash(f'حدث خطأ أثناء حذف الملف: {str(e)}', 'error')
        print(f"Error deleting file {file_path}: {e}")

    return redirect(request.referrer or url_for('show_classifications'))
