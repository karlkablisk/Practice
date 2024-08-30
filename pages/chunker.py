import streamlit as st
import re
import json

def get_text_chunks(text, verbose=True):
    if verbose:
        st.warning(f"Debug: The type of the input is {type(text)}")
        st.warning(f"Debug: The first 100 characters of the input are: {text[:100]}")

    chunks_with_metadata = []

    # Split by page markers and ensure valid text processing
    pages = re.split(r'\[end of page \d+\]\s*\[start of page \d+\]', text)
    for i, page in enumerate(pages, start=1):
        if page.strip():  # Ensure non-empty
            # Remove any remaining start/end markers
            cleaned_text = re.sub(r'\[start of page \d+\]', '', page).strip()
            cleaned_text = re.sub(r'\[end of page \d+\]', '', cleaned_text).strip()

            chunks_with_metadata.append({
                'text': cleaned_text,
                'metadata': {'page_number': str(i)}
            })

    # Convert list to JSON
    json_output = json.dumps(chunks_with_metadata, indent=4)

    if verbose:
        st.warning(f"JSON output created with {len(chunks_with_metadata)} entries.")

    return json_output

# Streamlit App
st.title("Text Chunker and JSON Converter")

# Example text
example_text = """
[start of page 1] This is the content of page 1. It has some text that is relevant to page 1. [end of page 1]
[start of page 2] This is the content of page 2. It has some text that is relevant to page 2. [end of page 2]
[start of page 3] This is the content of page 3. It has some text that is relevant to page 3. [end of page 3]
"""

# Display the example text
st.text_area("Example Text", example_text, height=200)

# Chunk the text and output JSON
if st.button("Chunk and Convert to JSON"):
    json_output = get_text_chunks(example_text)
    st.json(json_output)
