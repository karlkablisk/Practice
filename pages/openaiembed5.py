import os
import streamlit as st

# Individual imports from llama_index
from llama_index import VectorStoreIndex
from llama_index import SimpleDirectoryReader
from llama_index import StorageContext
from llama_index import ServiceContext

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
    PERSIST_DIR = "./storage"
    
    # Create the document list from the pasted text
    try:
        with open("temp.txt", "w") as f:
            f.write(document_text)
        documents = SimpleDirectoryReader("temp.txt").load_data()
        logger.info("Document loaded successfully with SimpleDirectoryReader")
    except Exception as e:
        logger.error("Failed to load document with SimpleDirectoryReader:", exc_info=True)
        st.error("An error occurred while loading the document.")
    
    try:
        if not os.path.exists(PERSIST_DIR):
            index = VectorStoreIndex.from_documents(documents)
            index.storage_context.persist(persist_dir=PERSIST_DIR)
            logger.info("Index created and stored successfully")
        else:
            storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
            index = VectorStoreIndex.load(storage_context=storage_context)
            logger.info("Index loaded successfully from storage")
        
        # Initialize the query engine
        query_engine = index.as_query_engine()
        logger.info("Query engine initialized successfully")

        # Input for the user's question
        user_query = st.text_input("Ask a question about the document:")

        # If the 'Submit' button is clicked, perform the query
        if st.button("Submit"):
            if user_query.strip():
                try:
                    response = query_engine.query(user_query)
                    st.success(f"Response: {response}")
                except Exception as e:
                    st.error(f"An error occurred during the query: {e}")
                    logger.error("Query failed:", exc_info=True)
            else:
                st.error("Please enter a valid question.")
    except Exception as e:
        logger.error("An error occurred during indexing or querying:", exc_info=True)
        st.error("An error occurred during indexing or querying.")
