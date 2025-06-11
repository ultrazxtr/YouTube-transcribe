pip install flask
pip install yt_dlp
pip install google.cloud
pip install os
from flask import Flask, request, jsonify
import yt_dlp
from google.cloud import speech
import os

app = Flask(__name__)

Set up Google Cloud Speech-to-Text credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path_to_your_credentials.json'

Create a client instance
client = speech.SpeechClient()

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    video_url = data['url']

    # Download audio from YouTube video
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Transcribe audio using Google Cloud Speech-to-Text
    with open('audio.mp3', 'rb') as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=48000,
        language_code='en-US',
    )

    response = client.recognize(config, audio)

    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript

    # Remove the audio file
    os.remove('audio.mp3')

    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(debug=True)
