from flask import Flask, render_template, request
import os
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'

# ✅ Создаем папки при запуске, если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def is_video_file(filename):
    return filename.lower().endswith(('.mp4', '.mov', '.avi', '.webm'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)

            processed_filename = 'processed_' + filename
            processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)

            shutil.copy(upload_path, processed_path)

            return render_template(
                'index.html',
                filename=filename,
                is_video=is_video_file(filename)
            )
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
