import os
import json
import streamlit as st
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Models for text generation
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

# Hardcoded parameters for test
test_model = "tts-1"
test_voice = "nova"
test_text_to_speak = "Test"
test_file_path = Path(__file__).parent / "test_audio.mp3"

# Streamlit UI for testing
st.title("Hardcoded TTS Voice Generation and Structured Dialogue with TTS")

# Button to generate and play audio for the hardcoded test
if st.button("Generate and Play Test Audio"):
    try:
        # Generate audio with hardcoded settings
        response = client.audio.speech.create(
            model=test_model,
            voice=test_voice,
            input=test_text_to_speak
        )
        response.stream_to_file(test_file_path)
        st.audio(str(test_file_path), format="audio/mp3")
        st.success("Audio generated and played successfully.")
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")

# Define the schema using Pydantic for multiple dialogues
class DialogueLine(BaseModel):
    speaker: str
    dialogue: str

class StructuredDialogue(BaseModel):
    dialogues: list[DialogueLine]

# Load speakers configuration
json_file = Path(__file__).parent / "speakers.json"
if json_file.exists():
    with open(json_file, 'r') as f:
        speakers = json.load(f)
else:
    speakers = {}

# Interface for structured dialogue
st.write("## Dialogue Structuring with TTS using GPT-4o")
input_text = st.text_area("Enter the conversation text here:")
generate_voice = st.checkbox("Generate Voices for Each Dialogue")

if st.button("Generate Structured Dialogue"):
    if input_text:
        prompt = (
            "Structure the following conversation, marking unspoken lines as narrator:\n" + input_text
        )
        try:
            completion = client.beta.chat.completions.parse(
                model=gptomini,
                messages=[
                    {"role": "system", "content": "Extract and structure the dialogue information."},
                    {"role": "user", "content": prompt},
                ],
                response_format=StructuredDialogue,
            )
            structured_dialogue = completion.choices[0].message.parsed
            st.write("### Parsed Dialogue:")
            for dialogue in structured_dialogue.dialogues:
                st.write(f"**Speaker**: {dialogue.speaker}")
                st.write(f"**Dialogue**: {dialogue.dialogue}")
                if generate_voice:
                    file_path = Path(__file__).parent / f"{dialogue.speaker}_audio.mp3"
                    speaker_info = speakers.get(dialogue.speaker, speakers.get("default"))
                    model_to_use = "tts-1"  # Always use tts-1 for generating voices
                    voice_to_use = speaker_info.get("voice", "nova")
                    try:
                        response = client.audio.speech.create(
                            model=model_to_use,
                            voice=voice_to_use,
                            input=dialogue.dialogue
                        )
                        response.stream_to_file(file_path)
                        st.audio(str(file_path), format="audio/mp3")
                    except Exception as e:
                        st.error(f"Failed to generate voice for {dialogue.speaker}: {e}")
            st.code(json.dumps(structured_dialogue.dict(), indent=2), language='json')
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter the conversation text.")
