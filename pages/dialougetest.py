import os
import json
import streamlit as st
from openai import OpenAI
from pathlib import Path

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Models for text generation
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

# Load speakers from JSON file
json_file_path = Path("speakers.json")
if json_file_path.exists():
    with open(json_file_path, 'r') as f:
        speakers = json.load(f)
else:
    speakers = {}

# Function to generate audio
def generate_audio(model, voice, text, file_path):
    try:
        # Verbose output to confirm parameters being used
        st.write(
            f"Generating audio with the following details:\n"
            f"Model: {model}\n"
            f"Voice: {voice}\n"
            f"Text: {text}\n"
            f"File Path: {file_path}\n"
        )

        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        response.stream_to_file(file_path)
        st.audio(str(file_path), format="audio/mp3")
        st.success("Audio generated and played successfully.")
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")

# Hardcoded parameters for test
test_model = "tts-1"
test_voice = "nova"
test_text_to_speak = "Test"
test_file_path = Path(__file__).parent / "test_audio.mp3"

# Streamlit UI
st.title("Hardcoded TTS Voice Generation and Structured Dialogue with TTS")

# Button to generate and play audio for the hardcoded test
if st.button("Generate and Play Test Audio"):
    generate_audio(test_model, test_voice, test_text_to_speak, test_file_path)

# Input text for structured dialogue
st.write("## Dialogue Structuring with TTS using GPT-4o")
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
                model=gptomini,
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
                    speaker_info = speakers.get(dialogue.speaker, speakers.get("default"))
                    if not speaker_info:
                        st.error(f"No speaker info found for '{dialogue.speaker}' and no default configured.")
                        continue

                    # Always use "tts-1" as the model, regardless of what's in the JSON
                    model_to_use = "tts-1"
                    voice_to_use = speaker_info.get("voice", "Unknown")
                    file_path = Path(__file__).parent / f"{dialogue.speaker}_audio.mp3"

                    # Generate the audio
                    generate_audio(model_to_use, voice_to_use, dialogue.dialogue, file_path)

            # Show the real structured output for TTS or other processes
            st.write("### Structured Output for Processing:")
            st.code(json.dumps(structured_dialogue.dict(), indent=2), language='json')

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter the conversation text.")
