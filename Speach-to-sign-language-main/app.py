from flask import Flask, render_template, request, send_from_directory
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip, concatenate_videoclips
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Upload folders
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def index():
    output_video = None
    recognized_text = None
    uploaded_audio = None  # <--- ADD THIS

    if request.method == 'POST':
        audio_file = request.files.get('audio')
        text_input = request.form.get('text_input')

        if text_input:
            recognized_text = text_input.strip()

        elif audio_file and audio_file.filename != '':
            audio_filename = secure_filename(audio_file.filename)
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            audio_file.save(audio_path)

            uploaded_audio = os.path.join('uploads', audio_filename)  # <--- SAVE this path to pass to template

            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                try:
                    recognized_text = recognizer.recognize_google(audio_data)
                    print(f"Recognized Text: {recognized_text}")
                except (sr.UnknownValueError, sr.RequestError):
                    recognized_text = ""

        if recognized_text:
            words = recognized_text.lower().split()
            clips = []

            for word in words:
                video_path = os.path.join('static', 'videos', f'{word}.mp4')
                if os.path.exists(video_path):
                    clips.append(VideoFileClip(video_path))

            if clips:
                final_clip = concatenate_videoclips(clips, method="compose")
                output_path = os.path.join(OUTPUT_FOLDER, 'final_video.mp4')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                output_video = 'output/final_video.mp4'

    return render_template('index.html', output_video=output_video, recognized_text=recognized_text, uploaded_audio=uploaded_audio)




@app.route('/static/output/<path:filename>')
def serve_output(filename):
    return send_from_directory('static/output', filename)

if __name__ == '__main__':
    app.run(debug=True)
