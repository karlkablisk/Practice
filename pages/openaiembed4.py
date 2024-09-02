import os
import streamlit as st
import openai
import faiss
import numpy as np
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document  # Correct import for Document
import tiktoken  # For token count
import json
from uuid import uuid4  # Import uuid4 for generating unique IDs


class OpenAIStreamlitApp:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    def analyze_metadata(self, text):
        """Analyze and create metadata for the given text."""
        metadata = {
            "length": len(text),
            "token_count": self.count_tokens(text),
            "has_toc": self.detect_table_of_contents(text),
            "page_count": self.detect_page_count(text),
        }
        st.warning(f"Metadata created: {json.dumps(metadata, indent=2)}")
        return metadata

    def detect_table_of_contents(self, text):
        """Detect if there's a table of contents and its structure."""
        patterns = ["Table of Contents", "Contents", "Chapter", "Section"]
        toc_detected = any(pattern in text for pattern in patterns)
        if toc_detected:
            st.warning("Table of Contents detected.")
        return toc_detected

    def detect_page_count(self, text):
        """Estimate the number of pages based on markers."""
        pages = text.count("[start of page")
        st.warning(f"Estimated page count: {pages}")
        return pages

    def count_tokens(self, text, model="text-embedding-ada-002"):
        """Count the number of tokens in the given text."""
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))

    def chunk_text(self, text):
        """Chunk the text and create metadata for each chunk."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)

        documents = []
        for chunk in chunks:
            metadata = self.analyze_metadata(chunk)
            documents.append(Document(page_content=chunk, metadata=metadata))

        st.warning(f"{len(chunks)} chunks created.")
        return documents

    def create_vectorstore(self, documents):
        """Create a FAISS vectorstore and add documents."""
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query("sample text")))
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        uuids = [str(uuid4()) for _ in range(len(documents))]  # Generate UUIDs for documents
        vector_store.add_documents(documents=documents, ids=uuids)
        st.warning("Vectorstore created and documents added.")
        return vector_store

    def search_vectorstore(self, vector_store, query):
        """Search the vectorstore for the most relevant chunks."""
        results = vector_store.similarity_search(query, k=3)
        for res in results:
            st.write(f"Chunk: {res.page_content} \nMetadata: {res.metadata}")

    def run(self):
        st.title("Document Analysis and Metadata with FAISS")

        text_input = st.text_area("Paste your document here", height=200)

        if st.button("Process Document"):
            if text_input:
                with st.spinner('Processing and chunking the document...'):
                    documents = self.chunk_text(text_input)
                    vector_store = self.create_vectorstore(documents)
                    
                    query = st.text_input("Enter your query:")
                    if query:
                        self.search_vectorstore(vector_store, query)
            else:
                st.write("Please paste a document to process.")


if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
