from flask import Flask, request, redirect, url_for,Blueprint
from werkzeug.utils import secure_filename
import os
bhav_bp=Blueprint("bhav",__name__)
UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv', 'jpg', 'jpeg', 'gif'}
import collections
import collections.abc
collections.Sequence = collections.abc.Sequence

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bhav_bp.route('/upload', methods=['POST'])
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

