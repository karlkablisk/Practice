import os
import streamlit as st
from openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Models for text generation
gpt35 = "gpt-3.5-turbo"
gpt4t = "gpt-4-turbo"
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

# Set the default model here
default_model = gptomini

class OpenAIRAGApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def load_pdf_text(self, pdf_file):
        """Extract text from a PDF file."""
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def perform_rag(self, documents, query, model):
        """Perform RAG using the loaded documents and the query."""
        index = VectorStoreIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        response = query_engine.query(query)
        return response

    def run(self):
        st.title('PDF/Text Input and AI Question Answering with RAG')

        # Choose between PDF or text input
        input_type = st.radio("Choose input type:", ("PDF File", "Text Input"))

        if input_type == "PDF File":
            uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
            if uploaded_file is not None:
                pdf_text = self.load_pdf_text(uploaded_file)
                documents = [Document(pdf_text)]
                st.success("PDF file successfully loaded and processed.")
            else:
                documents = None
                st.info("Please upload a PDF file.")

        else:
            text_input = st.text_area("Enter your text:")
            if text_input:
                documents = [Document(text_input)]
                st.success("Text input successfully processed.")
            else:
                documents = None
                st.info("Please enter some text.")

        query = st.text_input("Enter your question:")
        if st.button("Get Answer") and documents:
            if not query.strip():
                st.error("Please enter a question.")
            else:
                model_choice = st.selectbox(
                    "Choose GPT Model:", 
                    [gpt35, gpt4t, gpto, gptop, gptomini],
                    index=[gpt35, gpt4t, gpto, gptop, gptomini].index(default_model)
                )
                try:
                    response = self.perform_rag(documents, query, model_choice)
                    st.text_area("Generated Response:", value=response, height=300)
                    st.success("Answer generated successfully.")
                except Exception as e:
                    st.error(f"Error generating answer: {e}")

if __name__ == "__main__":
    app = OpenAIRAGApp()
    app.run()
