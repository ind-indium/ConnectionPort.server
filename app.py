from flask import Flask, request, jsonify, send_file
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory mapping of codes to files
file_registry = {}

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Save the file with a unique code
    unique_code = str(uuid.uuid4())[:8]
    filepath = os.path.join(UPLOAD_FOLDER, unique_code + '_' + file.filename)
    file.save(filepath)

    # Register the file
    file_registry[unique_code] = filepath

    return jsonify({'message': 'File uploaded successfully', 'code': unique_code}), 200

@app.route('/download/<code>', methods=['GET'])
def download_file(code):
    if code not in file_registry:
        return jsonify({'error': 'Invalid or expired code'}), 404

    filepath = file_registry[code]
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found on server'}), 404

    return send_file(filepath, as_attachment=True)

@app.route('/delete/<code>', methods=['DELETE'])
def delete_file(code):
    if code not in file_registry:
        return jsonify({'error': 'Invalid or expired code'}), 404

    filepath = file_registry.pop(code, None)
    if filepath and os.path.exists(filepath):
        os.remove(filepath)

    return jsonify({'message': 'File deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
