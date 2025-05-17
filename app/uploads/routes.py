import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    uploaded_files = request.files.getlist('file')
    if not uploaded_files:
        return jsonify(error="No files in the request"), 400
    
    uploaded_filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            uploaded_filenames.append(filename)
    
    if uploaded_filenames:
        return jsonify(message="Files uploaded successfully", uploaded_files=uploaded_filenames), 201
    else:
        return jsonify(error="No valid files uploaded"), 400
