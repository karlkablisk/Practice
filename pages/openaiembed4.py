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
        toc = self.extract_toc(text)
        section_info = self.extract_section_info(text)
        metadata = {
            "chapter": section_info.get("chapter"),
            "section": section_info.get("section"),
            "title": section_info.get("title"),
            "page": current_page
        }
        st.info(f"Metadata created: {metadata}")
        return metadata

    def extract_toc(self, text):
        toc_entries = []
        if "[start of toc]" in text.lower() and "[end of toc]" in text.lower():
            toc_text = re.search(r"\[start of toc\](.*?)\[end of toc\]", text, re.DOTALL).group(1)
            toc_lines = toc_text.split("\n")

            for line in toc_lines:
                match = re.match(r"(\d+(\.\d+)*\s.*\s\d+)", line)
                if match:
                    parts = line.rsplit(" ", 1)
                    title = parts[0].strip()
                    page = parts[1].strip()
                    if page.isdigit():
                        toc_entries.append({"title": title, "page": int(page)})
            return toc_entries
        return None

    def extract_section_info(self, text):
        """Extract section, chapter, and title information from the text."""
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
            metadata = self.analyze_metadata(chunk, current_page)
            documents.append(Document(page_content=chunk, metadata=metadata))
            st.info(f"Chunk {i + 1}: {chunk}\nMetadata: {metadata}")
            current_page += chunk.count("[start of page")

        st.info(f"Total {len(chunks)} chunks created.")
        return documents

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

    def search_context(self, contexts, query, model="text-embedding-3-small"):
        query_embedding = self.get_embedding(query, model=model)
        similarities = [
            1 - cosine(np.array(self.get_embedding(context, model=model)), np.array(query_embedding))
            for context in contexts
        ]
        top_index = np.argmax(similarities)
        return contexts[top_index]

    def count_tokens(self, text, model="gpt-4o-mini"):
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))

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
        prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

        Context:
        {context}

        Question: {question}
        """
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
                    st.subheader(f"Chunk {i + 1}")
                    st.write(f"**Content:** {doc.page_content}")
                    st.write(f"**Metadata:** {doc.metadata}")
                    st.markdown("---")

        if st.session_state.vector_store:
            query = st.chat_input("💬 Enter your question here:")
            if query:
                with st.spinner('🔍 Searching for relevant information...'):
                    contexts = [doc.page_content for doc in st.session_state.documents]
                    best_context = self.search_context(contexts, query)
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