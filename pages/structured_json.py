import os
import streamlit as st
from pydantic import BaseModel
from openai import OpenAI
from pathlib import Path
import json

from tts_voicegen import TTSVoiceGen

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize TTSVoiceGen
tts_voicegen = TTSVoiceGen(
    api_key=openai_api_key,
    tts_models=["tts-1", "tts-1-hd"],
    voices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
)

# Define the schema using Pydantic for multiple dialogues
class DialogueLine(BaseModel):
    speaker: str
    dialogue: str
    voice: bool

class StructuredDialogue(BaseModel):
    dialogues: list[DialogueLine]

# Streamlit app interface
st.title("Dialogue Structuring with TTS using GPT-4o")

# Speaker setup
st.write("## Add Speakers")
speaker_name = st.text_input("Speaker Name")
speaker_pic = st.text_input("Speaker Picture URL (optional)")
selected_voice_model = st.selectbox("Select Voice Model", tts_voicegen.tts_models)
selected_voice = st.selectbox("Select Voice", tts_voicegen.voices)

if st.button("Add Speaker"):
    if speaker_name:
        tts_voicegen.add_speaker(speaker_name, speaker_pic, selected_voice_model, selected_voice)
        st.success(f"Added speaker {speaker_name}")
    else:
        st.error("Please enter a speaker name.")

# Display the current speakers
st.write("### Current Speakers")
for speaker in tts_voicegen.list_speakers():
    st.write(f"- {speaker}")

# Input text
input_text = st.text_area("Enter the conversation text here:")

if st.button("Generate Structured Dialogue"):
    if input_text:
        # Prompt to send to the model
        prompt = (
            "Structure the following conversation, marking unspoken lines as narrator:\n"
            + input_text
        )

        try:
            # API call with structured output
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": "Extract and structure the dialogue information."},
                    {"role": "user", "content": prompt},
                ],
                response_format=StructuredDialogue,
            )
            
            # Access the parsed response
            structured_dialogue = completion.choices[0].message.parsed

            # Streamlit display for each dialogue
            st.write("### Parsed Dialogue:")
            for dialogue in structured_dialogue.dialogues:
                st.write(f"**Speaker**: {dialogue.speaker}")
                st.write(f"**Dialogue**: {dialogue.dialogue}")
                if dialogue.voice:
                    file_path = Path(__file__).parent / f"{dialogue.speaker}_audio.mp3"
                    tts_voicegen.generate_audio(dialogue.speaker, dialogue.dialogue, file_path)
                    st.audio(str(file_path), format="audio/mp3")

            # Show the real structured output for TTS or other processes
            st.write("### Structured Output for Processing:")
            st.code(json.dumps(structured_dialogue.dict(), indent=2), language='json')

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter the conversation text.")
