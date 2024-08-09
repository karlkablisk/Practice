import os
import streamlit as st
from pydantic import BaseModel
from openai import OpenAI
import json
from pathlib import Path
from pages.tts_voicegen import TTSVoiceGen

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

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

class StructuredDialogue(BaseModel):
    dialogues: list[DialogueLine]

# Streamlit app interface
st.title("Dialogue Structuring with TTS using GPT-4o")

# Input text
input_text = st.text_area("Enter the conversation text here:")

# Single checkbox for voice generation
generate_voice = st.checkbox("Generate Voices for Each Dialogue")

# Button to generate structured dialogue and optionally generate voices
if st.button("Generate Structured Dialogue"):
    if input_text:
        # Prompt to send to the model
        prompt = (
            "Structure the following conversation, marking unspoken lines as narrator:\n" + input_text
        )
        
        try:
            # API call with structured output
            completion = client.beta.chat.completions.parse(
                model="gptomini",
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
                if generate_voice:
                    file_path = Path(__file__).parent / f"{dialogue.speaker}_audio.mp3"
                    try:
                        # Generate voice using TTSVoiceGen, fallback to default if speaker not found
                        tts_voicegen.generate_audio(dialogue.speaker, dialogue.dialogue, file_path)
                        st.audio(str(file_path), format="audio/mp3")
                    except Exception as e:
                        speaker_info = tts_voicegen.get_speaker_info(dialogue.speaker)
                        error_details = (
                            f"Failed to generate voice for {dialogue.speaker}: {e}\n"
                            f"Attempted model: tts-1\n"
                            f"Attempted voice: {speaker_info.get('voice', 'Unknown') if speaker_info else 'Default voice'}\n"
                            f"Text attempted: \"{dialogue.dialogue}\"\n"
                            f"File path attempted: {file_path}"
                        )
                        st.error(error_details)

            # Show the real structured output for TTS or other processes
            st.write("### Structured Output for Processing:")
            st.code(json.dumps(structured_dialogue.dict(), indent=2), language='json')

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter the conversation text.")
