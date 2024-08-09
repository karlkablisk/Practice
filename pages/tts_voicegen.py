import os
import json
import streamlit as st
from pathlib import Path
from openai import OpenAI

class TTSVoiceGen:
    def __init__(self, api_key, voices=None, json_file="speakers.json"):
        self.client = OpenAI(api_key=api_key)
        self.voices = voices or ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.json_file = Path(json_file)
        self.speakers = self.load_speakers()
        self.model = "tts-1"  # Hardcoded model, always tts-1

    def load_speakers(self):
        if self.json_file.exists():
            with open(self.json_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_speakers(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.speakers, f, indent=2)

    def add_speaker(self, name, pic, selected_model="openai", voice="nova"):
        if selected_model != "openai":
            raise ValueError(f"Unsupported TTS service: {selected_model}")
        if voice not in self.voices:
            raise ValueError(f"Invalid voice: {voice}")
        
        self.speakers[name] = {
            "pic": pic,
            "selected_model": selected_model,  # Store selected_model, even though it’s always "openai" for now
            "voice": voice
        }
        self.save_speakers()

    def generate_audio(self, speaker_name, text, file_path):
        if speaker_name not in self.speakers:
            raise ValueError(f"Speaker {speaker_name} not found.")
        
        speaker = self.speakers[speaker_name]
        if speaker["selected_model"] != "openai":
            raise ValueError(f"Unsupported TTS service: {speaker['selected_model']}")

        voice = speaker["voice"]

        try:
            response = self.client.audio.speech.create(
                model=self.model,  # Always use tts-1
                voice=voice,
                input=text
            )
            response.stream_to_file(file_path)
            return file_path
        except Exception as e:
            raise RuntimeError(f"Failed to generate audio for {speaker_name}: {e}")

    def list_speakers(self):
        return list(self.speakers.keys())

    def get_speaker_info(self, speaker_name):
        return self.speakers.get(speaker_name, None)

# If running directly, show the management interface
if __name__ == "__main__":
    # Load OpenAI API key from the environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize TTSVoiceGen
    tts_voicegen = TTSVoiceGen(
        api_key=openai_api_key,
        voices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    )
    
    st.title("TTS Voice Generator Management")

    # Show existing speakers
    st.write("## Current Speakers")
    for speaker_name, info in tts_voicegen.speakers.items():
        st.write(f"**{speaker_name}**")
        st.write(f"Selected Model: {info['selected_model']} | Voice: {info['voice']}")
        if info['pic']:
            st.image(info['pic'], width=100)

        # Test audio output
        if st.button(f"Test Voice for {speaker_name}"):
            test_text = f"Hi, I'm {speaker_name}"
            file_path = Path(__file__).parent / f"{speaker_name}_test_audio.mp3"
            try:
                tts_voicegen.generate_audio(speaker_name, test_text, file_path)
                st.audio(str(file_path), format="audio/mp3")
                st.success(f"Test audio generated successfully for {speaker_name}.")
            except Exception as e:
                st.error(f"Failed to generate test audio for {speaker_name}: {e}")

    st.write("## Add New Speaker")
    speaker_name = st.text_input("Speaker Name")
    speaker_pic = st.text_input("Speaker Picture URL (optional)")
    selected_model = st.selectbox("Select TTS Service", ["openai"])  # Only "openai" for now
    selected_voice = st.selectbox("Select Voice", tts_voicegen.voices)

    if st.button("Add Speaker"):
        if speaker_name:
            try:
                tts_voicegen.add_speaker(speaker_name, speaker_pic, selected_model, selected_voice)
                st.success(f"Added speaker {speaker_name}")
            except ValueError as e:
                st.error(f"Failed to add speaker: {e}")
        else:
            st.error("Please enter a speaker name.")
