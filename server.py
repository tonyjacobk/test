from flask import Flask, request, redirect, url_for,Blueprint,send_file
from werkzeug.utils import secure_filename
import os
bhav_bp=Blueprint("bhav",__name__)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bhav_bp.route('/bhavupload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join('/tmp', filename))
        return f'File {filename} uploaded successfully', 201
    else:
        return 'Invalid file type or no file selected', 400

@bhav_bp.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post action="/upload" enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''
@bhav_bp.route('/bhavtest')
def bhavtest():
    try:
        with open('price.csv', 'r', encoding='utf-8') as f:
            lines = []
            for _ in range(50):
                line = f.readline()
                if not line:
                    break
                lines.append(line.rstrip('\n'))
            return lines
    except FileNotFoundError:
        return "No file"
@bhav_bp.route('/bhavlist')
def list_tmp_files():
    path = "."
    try:
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        print("Files in /tmp:")
        return files
    except Exception as e:
      return (f"Error {e}")
