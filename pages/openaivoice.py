import os
import json
import streamlit as st
from pathlib import Path
from openai import OpenAI

class TTSVoiceGen:
    def __init__(self, api_key, tts_models=None, voices=None, json_file="speakers.json"):
        self.client = OpenAI(api_key=api_key)
        self.tts_models = tts_models or ["tts-1"]  # Default to "tts-1" if not provided
        self.voices = voices or ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        self.json_file = Path(json_file)
        self.speakers = self.load_speakers()

    def load_speakers(self):
        if self.json_file.exists():
            with open(self.json_file, 'r') as f:
                return json.load(f)
        else:
            return {}

    def save_speakers(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.speakers, f, indent=2)

    def add_speaker(self, name, pic, voice_model="tts-1", voice="nova"):
        # Store voice_model but always use "tts-1" in the generate_audio function
        self.speakers[name] = {
            "pic": pic,
            "voice_model": voice_model,
            "voice": voice,
            "service": "openai"
        }
        self.save_speakers()

    def generate_audio(self, speaker_name, text, file_path, verbose=True):
        if speaker_name not in self.speakers:
            raise ValueError(f"Speaker {speaker_name} not found.")
        
        speaker = self.speakers[speaker_name]
        model = "tts-1"
        voice = speaker["voice"]

        if verbose:
            diagnostic_info = (
                f"Attempting to generate audio with the following parameters:\n"
                f"Model: {model}\n"
                f"Voice: {voice}\n"
                f"Text: {text}\n"
                f"File Path: {file_path}\n"
            )
            st.warning(diagnostic_info)

        try:
            response = self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )
            response.stream_to_file(file_path)
            if verbose:
                st.success(f"Audio generated successfully with the following diagnostics:\n{diagnostic_info}")
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
        tts_models=["tts-1", "tts-1-hd"],
        voices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    )
    
    st.title("TTS Voice Generator Management")

    # Show existing speakers
    st.write("## Current Speakers")
    for speaker_name, info in tts_voicegen.speakers.items():
        st.write(f"**{speaker_name}**")
        st.write(f"Model: {info['voice_model']} | Voice: {info['voice']}")
        if info['pic']:
            st.image(info['pic'], width=100)

        # Test audio output
        if st.button(f"Test Voice for {speaker_name}"):
            test_text = f"Hi, I'm {speaker_name}"
            file_path = Path(__file__).parent / f"{speaker_name}_test_audio.mp3"
            try:
                tts_voicegen.generate_audio(speaker_name, test_text, file_path, verbose=True)
                st.audio(str(file_path), format="audio/mp3")
            except Exception as e:
                st.error(f"Failed to generate test audio for {speaker_name}: {e}")

    st.write("## Add New Speaker")
    speaker_name = st.text_input("Speaker Name")
    speaker_pic = st.text_input("Speaker Picture URL (optional)")
    selected_voice_model = st.selectbox("Select Voice Model", tts_voicegen.tts_models)
    selected_voice = st.selectbox("Select Voice", tts_voicegen.voices)

    if st.button("Add Speaker"):
        if speaker_name:
            try:
                tts_voicegen.add_speaker(speaker_name, speaker_pic, selected_voice_model, selected_voice)
                st.success(f"Added speaker {speaker_name}")
            except ValueError as e:
                st.error(f"Failed to add speaker: {e}")
        else:
            st.error("Please enter a speaker name.")
