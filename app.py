from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import datetime

app = Flask(__name__)
CORS(app)

FACES_FOLDER = 'faces'
os.makedirs(FACES_FOLDER, exist_ok=True)

def save_face_image(student_id, image_base64):
    try:
        header, encoded = image_base64.split(',', 1)
        image_data = base64.b64decode(encoded)
        filename = f"{student_id}.jpg"
        filepath = os.path.join(FACES_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False

@app.route('/api/register-face', methods=['POST'])
def register_face():
    data = request.get_json()
    student_id = data.get('studentId')
    image = data.get('image')
    
    if not student_id or not image:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
    
    if save_face_image(student_id, image):
        return jsonify({'success': True, 'message': 'Face registered successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to save image'}), 500

@app.route('/api/attendance', methods=['POST'])
def mark_attendance():
    data = request.get_json()
    student_id = data.get('studentId')
    timestamp = datetime.datetime.now().isoformat()
    
    print(f"Attendance marked for {student_id} at {timestamp}")
    return jsonify({'success': True, 'message': 'Attendance marked', 'time': timestamp})

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'Attendance Server Running'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
