from flask import Flask, render_template, request
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['PROCESSED_FOLDER'] = 'static/processed'

# Создание папок при необходимости
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

            if is_video_file(filename):
                # Для видео пока просто копируем
                import shutil
                shutil.copy(upload_path, processed_path)
            else:
                # Обработка изображения (шумоподавление)
                image = cv2.imread(upload_path)
                if image is not None:
                    denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
                    cv2.imwrite(processed_path, denoised)
                else:
                    return "Ошибка при чтении изображения. Убедитесь, что файл — это фото."

            return render_template(
                'index.html',
                filename=filename,
                is_video=is_video_file(filename)
            )
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)
