import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import subprocess
from subprocess import PIPE
import sys
sys.path.append('../models')
from keras.preprocessing import image as image_utils
from imagenet_utils import decode_predictions
from imagenet_utils import preprocess_input
from vgg16 import VGG16
from vgg19 import VGG19
from resnet50 import ResNet50
import numpy as np
import argparse
import cv2

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)

#images dictionary contains uuids and corresponding file path for each uuid
images = {}

#images dictionary must have at least one record
def get_actual_path(uuid):
	uuid= str(uuid)
	if(uuid in images):
	    return images[uuid]
	else:
	    return "Invalid uuid"

def predict_image(modelType, imagePath):
	print("[INFO] loading and preprocessing image...")
	image = image_utils.load_img(imagePath, target_size=(224, 224))
	image = image_utils.img_to_array(image)

	image = np.expand_dims(image, axis=0)
	image = preprocess_input(image)

	print("[INFO] loading network...")
	if(modelType == "ResNet50"):
		model = ResNet50(weights="imagenet")
	elif(modelType == "VGG16"):
		model = VGG16(weights="imagenet")
	elif(modelType == "VGG19"):
		model = VGG19(weights="imagenet")
	else:
		print("Invalid Usage!- Model Name doesnot exist")
		exit()

	print("[INFO] classifying image...")
	preds = model.predict(image)
	(inID, label) = decode_predictions(preds)[0]
	return label

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/analyze/<path:path>', methods=['GET'])
def analyze_image(path):
	IPath = get_actual_path(path)
	if(os.path.isfile(IPath)):
		value = predict_image("VGG16",IPath)
		response = jsonify({'message': value})
		response.status_code = 200
	elif(IPath=="Invalid uuid"):
		response = jsonify({'message': 'File not found'})
		response.status_code = 404
	else:
		response = jsonify({'message': 'File not found'})
		response.status_code = 404
	return response
	
if __name__ == '__main__':
    app.run(debug=True)
