from flask import Flask, request, render_template, jsonify, send_file
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ImageClip
from tqdm import tqdm  # Для отслеживания прогресса

app = Flask(__name__)

# Глобальная переменная для хранения прогресса
progress = 0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/progress')
def get_progress():
    return jsonify({"progress": progress})

@app.route('/generate_video', methods=['POST'])
def generate_video():
    global progress
    progress = 0  # Сброс перед началом рендеринга

    # Получение данных из формы
    video_data = {
        "date": request.form["date"],
        "time": request.form["time"],
        "team1_image": request.files["team1_image"],
        "bottom_text": request.form["bottom_text"],
        "button_text": request.form["button_text"],
    }

    # Сохранение изображения временно
    video_data["team1_image"].save("team1_image.jpg")

    # Загрузка базового видео-шаблона
    base_clip = VideoFileClip("15921892-uhd_3840_2160_50fps.mp4")

    # Создание текстовых клипов
    date_text = TextClip(video_data["date"], fontsize=70, color='white')
    time_text = TextClip(video_data["time"], fontsize=70, color='white')
    bottom_text = TextClip(video_data["bottom_text"], fontsize=50, color='white')
    button_text = TextClip(video_data["button_text"], fontsize=50, color='yellow')

    # Длительность и позиции
    date_text = date_text.set_start(3).set_duration(5)
    time_text = time_text.set_start(3).set_duration(5)
    bottom_text = bottom_text.set_start(3).set_duration(5)
    button_text = button_text.set_start(3).set_duration(5)

    video_width = base_clip.size[0]
    video_height = base_clip.size[1]
    margin = 30

    date_text = date_text.set_pos((video_width - date_text.w - margin, margin))
    time_text = date_text.set_pos((video_width - time_text.w - margin, date_text.h + 2*margin))
    bottom_text = bottom_text.set_pos((margin, video_height - bottom_text.h - margin))
    button_text = button_text.set_pos(('center', 'bottom'))

    # Создание изображения и объединение клипов
    team1_image_clip = ImageClip("team1_image.jpg").set_start(5).set_duration(base_clip.duration - 5).set_position("center")

    final_clip = CompositeVideoClip([base_clip, team1_image_clip, date_text, time_text, bottom_text, button_text])

    # Рендеринг файла в один этап
    output_file = "final_output.mp4"

    with tqdm(total=int(final_clip.duration * 30), desc="Rendering Video") as pbar:
        final_clip.write_videofile(output_file, codec='libx264', audio_codec='aac', threads=4)

    return render_template("result.html", download_link="/download_video")

@app.route('/download_video')
def download_video():
    return send_file("final_output.mp4", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
