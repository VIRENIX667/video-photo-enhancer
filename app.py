import os
import uuid
import subprocess
from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi'}


def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTENSIONS.union(VIDEO_EXTENSIONS)


def process_video(input_path, output_path):
    cmd = [
        'ffmpeg',
        '-i', input_path,
        '-vf', 'hqdn3d,unsharp=5:5:1.0:5:5:0.0,eq=contrast=1.1:brightness=0.05',
        '-c:v', 'libx265',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_path
    ]
    subprocess.run(cmd, check=True)


def process_image(input_path, output_path):
    import cv2
    img = cv2.imread(input_path)
    dst = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
    sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    dst = cv2.filter2D(dst, -1, sharpen_kernel)
    cv2.imwrite(output_path, dst)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)

            ext = os.path.splitext(filename)[1].lower()
            output_filename = f"enhanced_{uuid.uuid4().hex}{ext}"
            output_path = os.path.join(PROCESSED_FOLDER, output_filename)

            try:
                if ext in VIDEO_EXTENSIONS:
                    process_video(input_path, output_path)
                else:
                    process_image(input_path, output_path)
            except Exception as e:
                return f"<h3>Ошибка обработки файла: {e}</h3>"

            return redirect(url_for('download_file', filename=output_filename))

    return render_template('index.html')


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(PROCESSED_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
