import os
import numpy as np
import cv2
import pytesseract
import matplotlib.pyplot as plt
from flask import Flask, request, redirect, url_for, send_from_directory,render_template
from PIL import Image,ImageFilter

UPLOAD_FOLDER = 'C:/Users/balar/OneDrive/Desktop/sample1/uploads'
CROP_FOLDER = 'C:/Users/balar/OneDrive/Desktop/sample1/crop'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CROP_FOLDER'] = CROP_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template("upload.html")

@app.route('/register',methods=['GET','POST'])
def register():
    return render_template('register.html')

@app.route('/show/<filename>')
def uploaded_file(filename):
    img = cv2.imread('uploads/'+filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY,11,2)
    contours,h = cv2.findContours(thresh,1,2)
    largest_rectangle = [0,0]
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
        if len(approx)==4:
            area = cv2.contourArea(cnt)
            if area > largest_rectangle[0]:
                largest_rectangle = [cv2.contourArea(cnt), cnt, approx]
    x,y,w,h = cv2.boundingRect(largest_rectangle[1])
    roi=img[y:y+h,x:x+w]
    img = Image.fromarray(roi, 'RGB')
    img = img.filter(ImageFilter.SHARPEN)
    img.save(os.path.join(app.config['CROP_FOLDER'], filename))
    filename = 'http://127.0.0.1:5000/crop/' + filename
    return render_template('template.html', filename=filename)

@app.route('/crop/<filename>')
def send_file(filename):
    return send_from_directory(CROP_FOLDER, filename)



if __name__ == '__main__':
    app.run()