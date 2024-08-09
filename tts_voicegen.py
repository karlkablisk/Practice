import os
from openai import OpenAI
from pathlib import Path

class TTSVoiceGen:
    def __init__(self, api_key, tts_models, voices):
        self.client = OpenAI(api_key=api_key)
        self.tts_models = tts_models
        self.voices = voices
        self.speakers = {}

    def add_speaker(self, name, pic, voice_model, voice):
        self.speakers[name] = {
            "pic": pic,
            "voice_model": voice_model,
            "voice": voice
        }

    def generate_audio(self, speaker_name, text, file_path):
        if speaker_name not in self.speakers:
            raise ValueError(f"Speaker {speaker_name} not found.")
        
        speaker = self.speakers[speaker_name]
        response = self.client.audio.speech.create(
            model=speaker["voice_model"],
            voice=speaker["voice"],
            input=text
        )
        response.stream_to_file(file_path)
        return file_path

    def list_speakers(self):
        return list(self.speakers.keys())

    def get_speaker_info(self, speaker_name):
        return self.speakers.get(speaker_name, None)
