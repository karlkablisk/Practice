import streamlit as st
import openai
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores import SimpleVectorStore  # Remove this import if it's causing an issue
from llama_index.llms.openai import OpenAI
import os
from dotenv import load_dotenv

# Initialize the OpenAI client with the API key from the environment variable
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key:
    openai.api_key = openai_api_key
else:
    st.error("API key not found. Please set your OPENAI_API_KEY environment variable.")

st.set_page_config(page_title="Chat with Custom Text, powered by LlamaIndex", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)

st.title("Chat with Custom Text, powered by LlamaIndex 💬🦙")
st.info("Paste any text and ask questions about it.", icon="📃")

if "messages" not in st.session_state.keys():  # Initialize the chat messages history
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Please paste your text in the input box and ask me a question!",
        }
    ]

# Initialize the embedding model
embedding_model = OpenAIEmbedding(model="text-embedding-3-small")

@st.cache_resource(show_spinner=False)
def create_index_from_text(pasted_text):
    # Convert the pasted text into a Document format required by LlamaIndex
    document = Document(text=pasted_text)
    
    # Create a vector store index using the specified embedding model
    index = VectorStoreIndex.from_documents([document], embedding_model=embedding_model)
    
    return index

# Text input box for the user to paste their text
pasted_text = st.text_area("Paste your text here:")

if pasted_text:
    index = create_index_from_text(pasted_text)
else:
    index = None

if index is None:
    st.stop()

# Initialize the chat engine with the specified LLM
if "chat_engine" not in st.session_state.keys():
    Settings.llm = OpenAI(
        model="gpt-4o-mini",
        temperature=0.2,
        system_prompt="""You are an expert on the provided text document. 
        Your job is to answer questions based on the content of this document. 
        Keep your answers factual and related to the text. Do not provide information outside of the document's content.""",
    )
    st.session_state.chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True, streaming=True
    )

# Prompt for user input and save to chat history
if prompt := st.chat_input("Ask a question based on the pasted text"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# Write message history to UI
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If the last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        response_stream = st.session_state.chat_engine.stream_chat(prompt)
        st.write_stream(response_stream.response_gen)
        message = {"role": "assistant", "content": response_stream.response}
        st.session_state.messages.append(message)
