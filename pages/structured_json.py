import os
import streamlit as st
from pydantic import BaseModel
from openai import OpenAI
import json

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Define the schema using Pydantic for multiple dialogues
class DialogueLine(BaseModel):
    speaker: str
    dialogue: str

class StructuredDialogue(BaseModel):
    dialogues: list[DialogueLine]

# Streamlit app interface
st.title("Dialogue Structuring with GPT-4o")

# Input text
input_text = st.text_area("Enter the conversation text here:")

#models
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

if st.button("Generate Structured Dialogue"):
    if input_text:
        # Prompt to send to the model
        prompt = (
            "Structure the following conversation, marking unspoken lines as narrator. omit lines with no spoken text.:\n"
            + input_text
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

            # Show the real structured output for TTS or other processes
            st.write("### Structured Output for Processing:")
            st.code(json.dumps(structured_dialogue.dict(), indent=2), language='json')

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")
    else:
        st.warning("Please enter the conversation text.")
