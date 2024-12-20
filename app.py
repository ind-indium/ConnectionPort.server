import os
import random
import string
from flask import Flask, request, jsonify, send_file, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = "uploads"
TEXT_FOLDER = "texts"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEXT_FOLDER, exist_ok=True)

def generate_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

@app.route('/testing')
def testingfunc():
    return "<h1><big>Testing ok</big></h1>"
    
@app.route('/upload', methods=['POST'])
def upload():
    code = generate_code()
    text = request.form.get('text', None)  # Ensure `text` defaults to None if not provided
    file = request.files.get('file')

    if text and not file:
        text_path = os.path.join(TEXT_FOLDER, f"{code}.txt")
        with open(text_path, "w") as f:
            f.write(text)
        return jsonify({"message": "Text shared successfully", "code": code}), 200
    
    if file and not text:
        file_path = os.path.join(UPLOAD_FOLDER, f"{code}_{file.filename}")
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "code": code}), 200

    if text and file:
        text_path = os.path.join(TEXT_FOLDER, f"{code}.txt")
        with open(text_path, "w") as f:
            f.write(text)
        file_path = os.path.join(UPLOAD_FOLDER, f"{code}_{file.filename}")
        file.save(file_path)
        return jsonify({"message": "Both text and file shared successfully", "code": code}), 200

    return jsonify({"error": "No text or file provided"}), 400


@app.route('/download/<code>', methods=['GET'])
def download(code):
    # Locate file or text based on the code
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(code):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if filename.endswith('_text.txt'):  # Serve text as JSON
                with open(file_path, 'r') as f:
                    text_content = f.read()
                return jsonify({'message': 'Text retrieved successfully', 'text': text_content}), 200
            else:  # Serve file as an attachment
                return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'Code not found'}), 404

@app.route('/delete/<code>', methods=['DELETE'])
def delete(code):
    text_path = os.path.join(TEXT_FOLDER, f"{code}.txt")
    if os.path.exists(text_path):
        os.remove(text_path)
        return jsonify({"message": "Text deleted successfully"})
    
    for file in os.listdir(UPLOAD_FOLDER):
        if file.startswith(code):
            os.remove(os.path.join(UPLOAD_FOLDER, file))
            return jsonify({"message": "File deleted successfully"})
    
    return jsonify({"error": "Code not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
