from flask import Flask, request, send_file, render_template
from fpdf import FPDF
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# 업로드 폴더가 존재하지 않으면 생성
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400

    if file and file.filename.lower().endswith('.jpg'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            pdf_path = convert_to_pdf(file_path)
            return send_file(pdf_path, as_attachment=True, download_name='converted.pdf')
        except Exception as e:
            app.logger.error(f"Error converting file: {e}")
            return str(e), 500

    return 'Invalid file format', 400

def convert_to_pdf(jpg_path):
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # PDF 페이지에 이미지 추가
        pdf.image(jpg_path, x=10, y=8, w=190)
        
        pdf_path = jpg_path.replace('.jpg', '.pdf')
        pdf.output(pdf_path)
        
        if not os.path.exists(pdf_path):
            raise Exception("PDF 파일 생성 실패")
        
        return pdf_path
    except Exception as e:
        app.logger.error(f"Error creating PDF: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
