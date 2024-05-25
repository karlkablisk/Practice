import openai
import os
import cv2
import base64
from dotenv import load_dotenv
import requests
from moviepy.editor import VideoFileClip
from playsound import playsound
from faster_whisper import WhisperModel

# Load API key from .env file
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize Whisper model
model = WhisperModel("large-v2", device="cuda", compute_type="float16")

def extract_frames(video_file_path, frame_interval=50):
    video = cv2.VideoCapture(video_file_path)
    base64_frames = []
    timestamps = []
    frame_count = 0
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        if frame_count % frame_interval == 0:
            _, buffer = cv2.imencode(".jpg", frame)
            base64_frames.append(base64.b64encode(buffer).decode("utf-8"))
            timestamps.append(video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)  # Convert to seconds
        frame_count += 1
    video.release()
    return base64_frames, timestamps

def transcribe_audio_from_video(video_file_path):
    video = VideoFileClip(video_file_path)
    audio_file = "extracted_audio.wav"
    video.audio.write_audiofile(audio_file)
    
    segments, info = model.transcribe(audio_file, beam_size=5, word_timestamps=True)
    return segments, info

def match_frames_with_transcription(base64_frames, timestamps, segments):
    prompt_content = [
        "These are frames and the associated transcript from a video. Explain what you see in the order the events transpire."
    ]
    word_index = 0
    for frame, timestamp in zip(base64_frames, timestamps):
        prompt_content.append({"image": frame, "resize": 768})
        while word_index < len(segments) and segments[word_index].start <= timestamp:
            prompt_content.append(segments[word_index].text)
            word_index += 1
    return prompt_content

def get_video_description_and_voiceover(prompt_content):
    prompt_messages = [
        {
            "role": "user",
            "content": prompt_content,
        },
    ]
    params = {
        "model": "gpt-4o",
        "messages": prompt_messages,
        "max_tokens": 500,
    }
    result = client.chat.completions.create(**params)
    return result.choices[0].message.content

def generate_voiceover(script):
    response = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        },
        json={
            "model": "tts-1",
            "input": script,
            "voice": "shimmer",
        },
    )
    audio = b""
    for chunk in response.iter_content(chunk_size=1024 * 1024):
        audio += chunk
    with open("voiceover.mp3", "wb") as audio_file:
        audio_file.write(audio)
    playsound("voiceover.mp3")
    print("Voiceover generated and saved as voiceover.mp3")

if __name__ == "__main__":
    video_path = "conantest.mp4"
    base64_frames, timestamps = extract_frames(video_path)

    print("Transcribing audio from video...")
    segments, info = transcribe_audio_from_video(video_path)
    transcription_text = "\n".join([segment.text for segment in segments])
    print("Transcription of the audio:")
    print(transcription_text)

    with open("sound-transcript.txt", "w") as transcription_file:
        transcription_file.write(transcription_text)

    print("Matching frames with transcription...")
    prompt_content = match_frames_with_transcription(base64_frames, timestamps, segments)

    print("Generating video description and voiceover script...")
    description_and_script = get_video_description_and_voiceover(prompt_content)
    print("Description of the video and voiceover script:")
    print(description_and_script)

    with open("description.txt", "w") as text_file:
        text_file.write(description_and_script)

    print("Generating voiceover audio...")
    generate_voiceover(description_and_script)
