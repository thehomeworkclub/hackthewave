from flask import *
import os
import numpy as np
from keras.preprocessing import image
from keras.applications.vgg16 import VGG16, preprocess_input
from scipy.spatial import distance

model_vgg16 = VGG16(weights='imagenet', include_top=False)


def extract_features(img_path, model):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    expanded_img_array = np.expand_dims(img_array, axis=0)
    preprocessed_img = preprocess_input(expanded_img_array)
    features = model.predict(preprocessed_img)
    return features.flatten()


# Directory containing whale images
whale_dir = "./wales"

# Extracting features for each whale image and storing them in a list
whale_features = []
for img_file in os.listdir(whale_dir):
    img_path = os.path.join(whale_dir, img_file)
    try:
        whale_features.append(extract_features(img_path, model_vgg16))
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

whale_features = np.array(whale_features)


def contains_whale(input_img_path, model, stored_features, threshold=0.5):
    input_features = extract_features(input_img_path, model)

    # Compute distances between input features and stored features
    distances = np.linalg.norm(stored_features - input_features, axis=1)

    # If minimum distance is below threshold, the image contains a whale
    if np.min(distances) < threshold:
        return True
    return False


def check_for_whale(img_path):
    try:
        return contains_whale(img_path, model_vgg16, whale_features)
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return False


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    req = request.files['image']
    req.save('./static/img.jpg')
    imgrtn = check_for_whale('./static/img.jpg')
    print(imgrtn)
    return {"success": True, "data": imgrtn}


if __name__ == "__main__":
    app.run(debug=True)
