import os
import streamlit as st
try:
    from llama_index import VectorStoreIndex
    print("LlamaIndex imported successfully")
except ImportError as e:
    print("Failed to import LlamaIndex:", e)
    print("Check the installed packages with `pip list` and ensure LlamaIndex is correctly installed.")


from llama_index.llms import OpenAI
import openai
from dotenv import load_dotenv

# Load environment variables (including the OpenAI API key)
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit application title
st.title("Document Search with LlamaIndex and GPT-4o-mini")

# Text area to input the document
document_text = st.text_area("Paste your document here:", height=300)

# If the text area is not empty, process the document
if document_text:
    # Set up the LlamaIndex components
    PERSIST_DIR = "./storage"
    
    # Create the document list from the pasted text
    with open("temp.txt", "w") as f:
        f.write(document_text)
    documents = SimpleDirectoryReader("temp.txt").load_data()
    
    if not os.path.exists(PERSIST_DIR):
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = VectorStoreIndex.load(storage_context=storage_context)

    # Initialize the query engine
    query_engine = index.as_query_engine()

    # Input for the user's question
    user_query = st.text_input("Ask a question about the document:")

    # If the 'Submit' button is clicked, perform the query
    if st.button("Submit"):
        if user_query.strip():
            try:
                response = query_engine.query(user_query)
                st.success(f"Response: {response}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please enter a valid question.")

