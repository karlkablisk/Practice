import os
import streamlit as st
from openai import OpenAI
from pathlib import Path

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# List of OpenAI voices
voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# List of available TTS models
tts_models = ["tts-1", "tts-1-hd"]

# Function to generate audio from text
def generate_audio(text, voice, model, file_path):
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )
    response.stream_to_file(file_path)
    return file_path

# Streamlit UI
st.title("OpenAI Text-to-Speech (TTS) with Voice and Model Selection")

# Select a TTS model
selected_model = st.selectbox("Select a TTS model:", tts_models)

# Select a voice
selected_voice = st.selectbox("Select a voice:", voices)

# Text input
input_text = st.text_area("Enter text to synthesize:", value="Hello, world! This is a voice test.")

# Set the output audio file path
output_file_path = Path(__file__).parent / "generated_audio.mp3"

# Button to generate and stream audio
if st.button("Generate and Play Audio"):
    if not input_text.strip():
        st.error("Please enter some text.")
    else:
        try:
            audio_path = generate_audio(input_text, selected_voice, selected_model, output_file_path)
            st.audio(str(audio_path), format="audio/mp3")
            st.success("Audio generated successfully.")
        except Exception as e:
            st.error(f"Error generating audio: {e}")
