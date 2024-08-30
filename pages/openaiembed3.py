import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to get embeddings
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model).data[0].embedding

# Function to search for the most relevant context
def search_context(contexts, query):
    query_embedding = get_embedding(query, model='text-embedding-3-small')
    similarities = [1 - cosine(np.array(get_embedding(context)), query_embedding) for context in contexts]
    top_index = np.argmax(similarities)
    return contexts[top_index]

# Function to generate the answer
def generate_answer(context, question):
    prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

    Context:
    {context}

    Question: {question}
    """
    response = openai.Completion.create(
        model="text-davinci-003",  # Use the appropriate model for completion
        prompt=prompt,
        max_tokens=150,
        temperature=0
    )
    return response.choices[0].text.strip()

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
