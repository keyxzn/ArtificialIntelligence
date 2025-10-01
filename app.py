# import library
import os
import numpy as np
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
from PIL import Image, UnidentifiedImageError, ImageOps
from flask_cors import CORS
from io import BytesIO


# initialize flask
app = Flask(__name__, static_folder='static')

CORS(app)


# load model
model = load_model('model/defores4.h5')

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'tif', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')


# POST
@app.route('/predict', methods=['POST'])
def predict():
    print("Received a POST request")

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Unsupported file type'}), 400

    try:
        # save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # open the uploaded image
        img = Image.open(file_path)

        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # preprocess, resize to 512, 512
        original_size = img.size
        ratio = min(512 / original_size[0], 512 / original_size[1])
        new_size = (int(original_size[0] * ratio), int(original_size[1] * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

        new_img = Image.new("RGBA", (512, 512), (255, 255, 255, 255))
        new_img.paste(img, ((512 - new_size[0]) // 2, (512 - new_size[1]) // 2))


        new_img_array = np.array(new_img)

        valid_area_mask = Image.new("L", (512, 512), 0)  # create a blank mask
        draw = Image.new("L", new_size, 255)  # draw the valid area
        valid_area_mask.paste(draw, ((512 - new_size[0]) // 2, (512 - new_size[1]) // 2))
        valid_area_mask = np.array(valid_area_mask) > 0 

        # predict
        img_array = np.array(new_img) / 255.0  # normalize
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array)

        prediction = (prediction.squeeze() > 0.5).astype(np.uint8)


        prediction_resized = Image.fromarray(prediction * 255)
        prediction_resized = prediction_resized.resize(original_size, Image.Resampling.LANCZOS)
        prediction_resized_array = np.array(prediction_resized) / 255.0


        valid_area_mask_resized = Image.fromarray(valid_area_mask.astype(np.uint8) * 255)
        valid_area_mask_resized = valid_area_mask_resized.resize(original_size, Image.Resampling.NEAREST)
        valid_area_mask_resized = np.array(valid_area_mask_resized) > 0 


        valid_pixels = np.sum(valid_area_mask_resized) 
        deforested_valid_pixels = np.sum(prediction_resized_array[valid_area_mask_resized] < 0.5)  
        deforested_percentage = (deforested_valid_pixels / valid_pixels) * 100 if valid_pixels > 0 else 0


        print(f"Deforested Area Percentage: {deforested_percentage:.2f}%")

        # convert binary mask to an image
        mask_img = Image.fromarray((1- prediction) * 255)  # convert to 0-255 scale
        mask_img = mask_img.convert("L")  # convert to grayscale

        # save the mask image
        mask_path = os.path.join(app.config['UPLOAD_FOLDER'], 'mask.png')
        mask_img.save(mask_path)

        # Return the URLs of both images (original and mask) for the output
        return jsonify({
            'message': 'Prediction successful',
            'original_image_url': f'/uploads/{filename}',
            'mask_image_url': f'/uploads/mask.png',
            'deforested_percentage': f'{deforested_percentage:.2f}%'
        })

    except UnidentifiedImageError:
        return jsonify({'error': 'Uploaded file is not a valid image'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
