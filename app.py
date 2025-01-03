from flask import Flask, request, jsonify, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for uploading videos
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "Video uploaded successfully", "filename": filename}), 200
    return jsonify({"error": "Invalid file format"}), 400

# Route for fetching a video
@app.route('/video/<filename>', methods=['GET'])
def get_video(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route for video list
@app.route('/video-list', methods=['GET'])
def get_video_list():
    video_files = os.listdir(app.config['UPLOAD_FOLDER'])
    video_list = [{"filename": video} for video in video_files if allowed_file(video)]
    return jsonify(video_list)

# HTML template (Embedded within Python)
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Video Upload</title>
</head>
<body>
    <h1>Upload a Video</h1>
    <form id="upload-form" enctype="multipart/form-data">
        <input type="file" id="video-file" name="file" accept="video/*">
        <button type="submit">Upload</button>
    </form>

    <h2>Videos</h2>
    <div id="videos-list"></div>

    <script>
        // Handle video upload
        document.getElementById('upload-form').onsubmit = async function(e) {
            e.preventDefault();
            let formData = new FormData();
            formData.append('file', document.getElementById('video-file').files[0]);

            let response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            let result = await response.json();
            if (result.message) {
                alert(result.message);
                loadVideos();  // Reload the video list after uploading
            } else {
                alert(result.error);
            }
        };

        // Fetch and display videos
        async function loadVideos() {
            let response = await fetch('/video-list');
            let videos = await response.json();
            let videosListDiv = document.getElementById('videos-list');
            videosListDiv.innerHTML = '';
            videos.forEach(video => {
                let videoElement = document.createElement('video');
                videoElement.setAttribute('controls', '');
                videoElement.src = '/video/' + video.filename;
                videosListDiv.appendChild(videoElement);
            });
        }

        loadVideos();  // Load videos when page loads
    </script>
</body>
</html>
"""

# Route to serve the main page (HTML)
@app.route('/')
def index():
    return render_template_string(html_template)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
