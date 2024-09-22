from flask import Flask, request, jsonify, send_file
import os
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import io
import uuid
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
CORS(app, supports_credentials=True, allow_headers=['Form-data', 'Authorization'], methods=['GET', 'POST', 'OPTIONS'])

UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'

# Create directories if not exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)

# Route to handle file upload and model processing
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # Check if the file is an allowed .h5 file
    if file.filename == '' or not file.filename.endswith('.h5'):
        return jsonify({"error": "Invalid file type, only .h5 files are allowed"}), 400

    # Save the .h5 file to the uploads directory
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Load the model
    try:
        model = load_model(file_path)
    except Exception as e:
        return jsonify({"error": f"Failed to load the model: {str(e)}"}), 500

    # Generate images using the model (dummy images in this example)
    generated_images = generate_images(model)

    # Return the URLs of generated images
    image_urls = [f"/generated/{img}" for img in generated_images]
    return jsonify({"generatedImages": image_urls})


# Dummy function to generate images using the loaded model
def generate_images(model):
    # Example of generating random images
    generated_image_paths = []
    for i in range(3):
        # Generate a dummy image (replace this with your model's inference logic)
        img = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
        
        # Save the image to the generated folder
        filename = f"{uuid.uuid4().hex}.png"
        path = os.path.join(GENERATED_FOLDER, filename)
        img.save(path)
        generated_image_paths.append(filename)

    return generated_image_paths


# Route to serve generated images
@app.route('/generated/<filename>')
def serve_generated_image(filename):
    path = os.path.join(GENERATED_FOLDER, filename)
    return send_file(path, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
