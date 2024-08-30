import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to get embeddings using the chat API
def get_embedding(text, model="gpt-4o-mini"):
    response = openai.chat_completions.create(
        model=model,
        messages=[{"role": "system", "content": "Generate an embedding for the following text."},
                  {"role": "user", "content": text}],
        functions=[{
            "name": "embeddings.create",
            "description": "Generate embeddings for the provided text.",
            "parameters": {
                "model": "text-embedding-3-small",
                "input": [text]
            }
        }]
    )
    return response.choices[0].message['function_call']['arguments']['embedding']

# Function to search for the most relevant context
def search_context(contexts, query, model="gpt-4o-mini"):
    query_embedding = get_embedding(query, model=model)
    similarities = [1 - cosine(np.array(get_embedding(context, model=model)), np.array(query_embedding)) for context in contexts]
    top_index = np.argmax(similarities)
    return contexts[top_index]

# Function to generate the answer
def generate_answer(context, question, model="gpt-4o-mini"):
    prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

    Context:
    {context}

    Question: {question}
    """
    response = openai.chat_completions.create(
        model=model,
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0
    )
    return response.choices[0].message['content']

# Streamlit App
st.title("Question Answering with OpenAI Embeddings")

# Input for context
st.write("Paste your text context(s) below. Separate different contexts with a blank line.")
text_input = st.text_area("Text Contexts", height=200)
contexts = text_input.split("\n\n")

# Input for the question
question = st.text_input("Enter your question:")

if st.button("Get Answer"):
    if contexts and question:
        with st.spinner('Searching for the most relevant context...'):
            best_context = search_context(contexts, question)
            with st.spinner('Generating the answer...'):
                answer = generate_answer(best_context, question)
                st.write("Answer:", answer)
    else:
        st.write("Please provide both contexts and a question.")
