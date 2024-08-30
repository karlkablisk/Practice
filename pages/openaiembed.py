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

    pages = re.split(r'\[end of page \d+\]\s*\[start of page \d+\]', text)
    for i, page in enumerate(pages, start=1):
        if page.strip():
            cleaned_text = re.sub(r'\[start of page \d+\]', '', page).strip()
            cleaned_text = re.sub(r'\[end of page \d+\]', '', cleaned_text).strip()
            chunks = text_splitter.split_text(cleaned_text)
            if chunks:
                grouped_chunks.append({
                    'metadata': {'page_number': str(i)},
                    'text_chunks': [chunk.strip() for chunk in chunks if chunk.strip()]
                })

    return grouped_chunks

def get_embeddings(text_chunks):
    embeddings = []
    for item in text_chunks:
        for text in item['text_chunks']:
            text = text.replace("\n", " ")
            response = client.embeddings.create(input=[text], model="text-embedding-3-small")
            if 'data' in response and response['data']:
                embeddings.append(response['data'][0]['embedding'])
            else:
                st.error(f"Failed to retrieve embeddings for text: {text}")
    return embeddings

# Streamlit interface setup
st.title("AI Text Processing with OpenAI Embeddings")

# Always visible text input
input_text = st.text_area("Input Text", height=200, value="Enter your text here...")

if st.button("Generate Embeddings and Test AI"):
    chunked_data = get_text_chunks_grouped_by_page(input_text, verbose=True)
    if chunked_data:
        embeddings = get_embeddings(chunked_data)
        if embeddings:
            st.success("Embeddings generated successfully.")
            # Example of using embeddings in an AI response (assuming a function that uses these embeddings)
            st.write("Embeddings:", embeddings)
        else:
            st.error("Failed to generate embeddings.")
    else:
        st.error("Failed to chunk and process the text.")

