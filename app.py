from flask import Flask, request, send_file, render_template
import yt_dlp
import os
import re
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)

def sanitize_filename(filename):
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    filename = re.sub(r'\xa0', ' ', filename)
    max_length = 255
    if len(filename) > max_length:
        filename = filename[:max_length]
    return secure_filename(filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    video_url = request.form['url']
    quality = request.form['quality']
    download_dir = 'downloads'
    
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    ydl_opts = {
        'format': quality,
        'merge_output_format': 'mp4',
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info_dict)
            sanitized_filename = sanitize_filename(filename)
            sanitized_file_path = os.path.join(download_dir, sanitized_filename)

            if os.path.exists(sanitized_file_path):
                os.remove(sanitized_file_path)

            os.rename(filename, sanitized_file_path)
            
            # تأخير بسيط قبل حذف الملف
            response = send_file(sanitized_file_path, as_attachment=True)
            time.sleep(1)  # تأخير بسيط لضمان أن عملية الإرسال قد اكتملت
            if os.path.exists(sanitized_file_path):
                os.remove(sanitized_file_path)
            return response
        
    except Exception as e:
        error_message = f"حدث خطأ أثناء تنزيل الفيديو: {str(e)}"
        print(error_message)  # طباعة الخطأ في وحدة التحكم
        return render_template('index.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
