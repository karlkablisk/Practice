import streamlit as st
import re
import json
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def get_text_chunks_grouped_by_page(text, verbose=True):
    if verbose:
        st.warning(f"Debug: The type of the input is {type(text)}")
        st.warning(f"Debug: The first 100 characters of the input are: {text[:100]}")

    grouped_chunks = []
    text_splitter = CharacterTextSplitter()

    # Split by page markers and ensure valid text processing
    pages = re.split(r'\[end of page \d+\]\s*\[start of page \d+\]', text)
    for i, page in enumerate(pages, start=1):
        if page.strip():  # Ensure non-empty
            cleaned_text = re.sub(r'\[start of page \d+\]', '', page).strip()
            cleaned_text = re.sub(r'\[end of page \d+\]', '', cleaned_text).strip()
            chunks = text_splitter.split_text(cleaned_text)

            if chunks:
                grouped_chunks.append({
                    'metadata': {'page_number': str(i)},
                    'text_chunks': [chunk.strip() for chunk in chunks if chunk.strip()]
                })

    if verbose:
        st.warning(f"JSON output created with {len(grouped_chunks)} entries.")
    return grouped_chunks

def get_embeddings(text_chunks):
    embeddings = []
    for item in text_chunks:
        for text in item['text_chunks']:
            text = text.replace("\n", " ")
            try:
                response = client.embeddings.create(input=[text], model="text-embedding-3-small")
                if 'data' in response and response['data']:
                    embeddings.append(response['data'][0]['embedding'])
                else:
                    st.error(f"Failed to retrieve embeddings for text: {text}")
                    st.write(f"Received response: {response}")
            except Exception as e:
                st.error(f"An error occurred while retrieving embeddings: {str(e)}")
                st.write(f"Failed text: {text}")
    return embeddings

# Streamlit interface
st.title("Text Processing and Embedding with OpenAI")

example_text = st.text_area("Input Text", height=200, value="Your example text goes here.")

chunked_data = None

if example_text:
    chunked_data = get_text_chunks_grouped_by_page(example_text, verbose=False)
    embeddings = get_embeddings(chunked_data)
    st.session_state['embeddings'] = embeddings
    st.success("Embeddings generated and stored in session state.")

query = st.chat_input("Enter your query:")
if query and 'embeddings' in st.session_state:
    # Placeholder for querying the embeddings
    st.write(f"Processing query: {query}")
    # Implement actual query processing logic
else:
    st.error("Please enter a query and ensure embeddings are generated.")

