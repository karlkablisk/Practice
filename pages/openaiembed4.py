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
from uuid import uuid4  # Import uuid4 for generating unique IDs
from scipy.spatial.distance import cosine  # For cosine similarity
import tiktoken  # For token count


class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    def detect_toc_with_gpt(self, text_excerpt, model="gpt-4o-mini"):
        """Use GPT-4o mini to determine if there is a Table of Contents."""
        prompt = f"""The following text is from the beginning of a document. Please determine if it contains a Table of Contents. Answer with 'True' or 'False'.

        Text:
        {text_excerpt}

        Does this text contain a Table of Contents?"""
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10  # Keep token usage minimal
        )
        
        answer = response.choices[0].message['content'].strip().lower()
        return answer == 'true'

    def analyze_metadata(self, text):
        """Analyze and create relevant metadata for the given text."""
        toc_text_excerpt = text[:1000]  # Limit to 1000 characters to be token-efficient
        has_toc = self.detect_toc_with_gpt(toc_text_excerpt)
        metadata = {
            "has_toc": has_toc,
            "pages": self.detect_pages(text),
        }
        st.info(f"Metadata created: {metadata}")
        return metadata

    def detect_pages(self, text):
        """Identify and map page numbers based on [start of page x] and [end of page x] markers."""
        page_mapping = {}
        current_page = None

        lines = text.split("\n")
        for line in lines:
            if "[start of page" in line:
                current_page = int(line.split(" ")[-1].strip("]"))
            elif "[end of page" in line:
                current_page = None
            if current_page is not None:
                if current_page not in page_mapping:
                    page_mapping[current_page] = []
                page_mapping[current_page].append(line)

        st.info(f"Pages detected: {list(page_mapping.keys())}")
        return page_mapping

    def chunk_text(self, text):
        """Chunk the text and create metadata for each chunk."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_text(text)

        documents = []
        for i, chunk in enumerate(chunks):
            metadata = self.analyze_metadata(chunk)
            documents.append(Document(page_content=chunk, metadata=metadata))
            st.info(f"Chunk {i + 1}: {chunk}\nMetadata: {metadata}")

        st.info(f"Total {len(chunks)} chunks created.")
        return documents

    def create_vectorstore(self, documents):
        """Create a FAISS vectorstore and add documents."""
        sample_embedding = self.embeddings.embed_query("sample text")
        embedding_dim = len(sample_embedding)
        index = faiss.IndexFlatL2(embedding_dim)
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        uuids = [str(uuid4()) for _ in range(len(documents))]  # Generate UUIDs for documents
        vector_store.add_documents(documents=documents, ids=uuids)
        st.info("Vectorstore created and documents added.")
        return vector_store

    def get_embedding(self, text, model="text-embedding-3-small"):
        """Generate an embedding for the input text."""
        response = openai.embeddings.create(
            input=[text],
            model=model
        )
        embedding = response.data[0].embedding
        st.write(f"Embedding summary: Length = {len(embedding)}, First 5 values = {embedding[:5]}")
        return embedding

    def search_context(self, contexts, query, model="text-embedding-3-small"):
        """Search the most relevant context based on the cosine similarity of embeddings."""
        query_embedding = self.get_embedding(query, model=model)
        similarities = [
            1 - cosine(np.array(self.get_embedding(context, model=model)), np.array(query_embedding))
            for context in contexts
        ]
        top_index = np.argmax(similarities)
        return contexts[top_index]

    def count_tokens(self, text, model="gpt-4o-mini"):
        """Count the number of tokens in the given text."""
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))

    def generate_text(self, prompt, model="gpt-4o-mini", max_tokens=1500):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        try:
            total_tokens = self.count_tokens(prompt, model=model) + max_tokens
            if total_tokens > 8192:  # Example limit, adjust based on your model
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
        """Generate an answer using the most relevant context."""
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
