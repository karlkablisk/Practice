import os
import streamlit as st
import openai
import faiss
import numpy as np
from langchain.docstore.in_memory import InMemoryDocstore
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from uuid import uuid4
from scipy.spatial.distance import cosine
import tiktoken
import re

class OpenAIStreamlitApp:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def analyze_metadata(self, text, current_page):
        section_info = self.extract_section_info(text)
        metadata = {
            "chapter": section_info.get("chapter"),
            "section": section_info.get("section"),
            "title": section_info.get("title"),
            "page": current_page
        }
        st.info(f"Metadata created: {metadata}")
        return metadata

    def extract_section_info(self, text):
        match = re.search(r"(\d+(\.\d+)*)\s+(.*)", text)
        if match:
            section_number = match.group(1)
            title = match.group(3).strip()
            chapter_number = section_number.split('.')[0] if '.' in section_number else section_number
            return {"chapter": chapter_number, "section": section_number, "title": title}
        return {"chapter": None, "section": None, "title": None}

    def chunk_text(self, text):
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)

        documents = []
        current_page = 1
        for i, chunk in enumerate(chunks):
            current_page = self.get_current_page(chunk, current_page)
            metadata = self.analyze_metadata(chunk, current_page)
            document = Document(page_content=chunk, metadata=metadata)
            documents.append(document)
            st.info(f"Chunk {i + 1}: {chunk}\nMetadata: {metadata}")
        
        st.info(f"Total {len(documents)} documents created.")
        return documents

    def get_current_page(self, chunk, current_page):
        """Update the current page based on the presence of page markers in the chunk."""
        start_page_markers = re.findall(r"\[start of page (\d+)\]", chunk)
        end_page_markers = re.findall(r"\[end of page (\d+)\]", chunk)

        if start_page_markers:
            current_page = int(start_page_markers[-1])
        elif end_page_markers:
            current_page = int(end_page_markers[-1]) + 1
        return current_page

    def create_vectorstore(self, documents):
        sample_embedding = self.embeddings.embed_query("sample text")
        embedding_dim = len(sample_embedding)
        index = faiss.IndexFlatL2(embedding_dim)
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)
        st.info("Vectorstore created and documents added.")
        return vector_store

    def get_embedding(self, text, model="text-embedding-3-small"):
        response = openai.embeddings.create(input=[text], model=model)
        embedding = response.data[0].embedding
        st.write(f"Embedding summary: Length = {len(embedding)}, First 5 values = {embedding[:5]}")
        return embedding

    def search_context(self, documents, query, model="text-embedding-3-small"):
        relevant_context = ""
        for doc in documents:
            if (query.lower() in doc.metadata.get("chapter", "").lower() or
                query.lower() in doc.metadata.get("section", "").lower() or
                query.lower() in doc.metadata.get("title", "").lower()):
                relevant_context += doc.page_content + "\n"

        if not relevant_context.strip():
            query_embedding = self.get_embedding(query, model=model)
            similarities = [
                1 - cosine(np.array(self.get_embedding(doc.page_content, model=model)), np.array(query_embedding))
                for doc in documents
            ]
            top_index = np.argmax(similarities)
            return documents[top_index].page_content

        return relevant_context.strip()

    def generate_text(self, prompt, model="gpt-4o-mini", max_tokens=1500):
        try:
            total_tokens = self.count_tokens(prompt, model=model) + max_tokens
            if total_tokens > 8192:
                raise ValueError(f"Total token count exceeds the model's limit: {total_tokens} tokens")

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except openai.error.OpenAIError as e:
            st.error(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            st.error(f"Error generating text: {str(e)}")

    def generate_answer(self, context, question, model="gpt-4o-mini"):
        prompt = f"""Based on the following context, answer the question as accurately as possible. If the answer isn't directly available, try to infer from the information provided.

        Context:
        {context}

        Question: {question}

        Provide the most relevant information available."""
    
        return self.generate_text(prompt, model=model)

    def run(self):
        st.title("📄 Document Analysis and Retrieval-Augmented Generation (RAG) with FAISS")

        if 'vector_store' not in st.session_state:
            st.session_state.vector_store = None
        if 'documents' not in st.session_state:
            st.session_state.documents = []

        with st.sidebar:
            st.header("Instructions")
            st.write("""
                1. **Paste your document** in the text area below.
                2. Click on **Process Document** to chunk and analyze it.
                3. **Ask questions** about the document using the chat input at the bottom.
            """)

        text_input = st.text_area("📋 Paste your document here", height=300)

        if st.button("✅ Process Document"):
            if text_input:
                with st.spinner('🔄 Processing and chunking the document...'):
                    documents = self.chunk_text(text_input)
                    vector_store = self.create_vectorstore(documents)
                    st.session_state.vector_store = vector_store
                    st.session_state.documents = documents
            else:
                st.warning("Please paste a document to process.")

        if st.session_state.documents:
            with st.expander("📄 Show Chunks and Metadata", expanded=True):
                for i, doc in enumerate(st.session_state.documents):
                    st.subheader(f"Document {i + 1}")
                    st.write(f"**Content:** {doc.page_content}")
                    st.write(f"**Metadata:** {doc.metadata}")
                    st.markdown("---")

        if st.session_state.vector_store:
            query = st.chat_input("💬 Enter your question here:")
            if query:
                with st.spinner('🔍 Searching for relevant information...'):
                    best_context = self.search_context(st.session_state.documents, query)
                with st.spinner('🤖 Generating answer...'):
                    answer = self.generate_answer(best_context, query)
                    if answer:
                        st.markdown(f"**Answer:** {answer}")
                    else:
                        st.markdown("**Answer:** Unable to generate an answer.")
        else:
            st.info("⚠️ Please process a document first to enable question answering.")


if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
