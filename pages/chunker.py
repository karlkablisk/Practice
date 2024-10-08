import streamlit as st
import re
import json

def get_text_chunks_grouped_by_page(text, verbose=True):
    if verbose:
        st.warning(f"Debug: The type of the input is {type(text)}")
        st.warning(f"Debug: The first 100 characters of the input are: {text[:100]}")

    grouped_chunks = []

    # Split by page markers and ensure valid text processing
    pages = re.split(r'\[end of page \d+\]\s*\[start of page \d+\]', text)
    for i, page in enumerate(pages, start=1):
        if page.strip():  # Ensure non-empty
            # Remove any remaining start/end markers
            cleaned_text = re.sub(r'\[start of page \d+\]', '', page).strip()
            cleaned_text = re.sub(r'\[end of page \d+\]', '', cleaned_text).strip()

            # Further chunk the text if it's too long for one chunk
            text_splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=500,  # Adjust chunk size as needed
                chunk_overlap=100,  # Adjust overlap as needed
                length_function=len
            )
            chunks = text_splitter.split_text(cleaned_text)

            # Group chunks under the same metadata
            if chunks:
                grouped_chunks.append({
                    'metadata': {'page_number': str(i)},
                    'text_chunks': [chunk.strip() for chunk in chunks if chunk.strip()]
                })

    # Convert list to JSON
    json_output = json.dumps(grouped_chunks, indent=4)

    if verbose:
        st.warning(f"JSON output created with {len(grouped_chunks)} entries.")

    return json_output

class CharacterTextSplitter:
    def __init__(self, separator="\n", chunk_size=500, chunk_overlap=100, length_function=len):
        self.separator = separator
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function

    def split_text(self, text):
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        return chunks

# Streamlit App
st.title("Text Chunker and JSON Converter")

# Example text input box
example_text = st.text_area("Example Text", height=200, value="""
[start of page 1] This is the beginning of page 1. It contains a lot of text, so much that it needs to be split into multiple chunks. 
Here is some more text to make sure that this page has more content than one chunk can handle. This should be enough for at least two chunks. 
[end of page 1]
[start of page 2] Page 2 starts here. It also contains a considerable amount of text. Let's add even more text to ensure this content is split into multiple chunks. 
More content is added to simulate a realistic scenario where the page is densely packed with information. [end of page 2]
[start of page 3] Page 3 is here. It has enough content to require multiple chunks as well. This allows us to test the chunking and embedding process more thoroughly. 
Adding more text here to create multiple chunks. Even more content follows to make sure that we have multiple chunks for page 3. 
[end of page 3]
""")

# Chunk the text and output JSON
if st.button("Chunk and Convert to JSON"):
    json_output = get_text_chunks_grouped_by_page(example_text)
    st.json(json_output)
