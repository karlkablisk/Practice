import os
import openai
import streamlit as st
import pandas as pd
import numpy as np
from openai.embeddings_utils import cosine_similarity

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to get embeddings
def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model).data[0].embedding

# Function to search for the most relevant context
def search_context(df, query, n=3):
    query_embedding = get_embedding(query, model='text-embedding-3-small')
    df['similarities'] = df.embedding.apply(lambda x: cosine_similarity(np.array(x), query_embedding))
    top_contexts = df.sort_values('similarities', ascending=False).head(n)
    return top_contexts['context'].values

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

# Load data
@st.cache
def load_data():
    df = pd.read_csv('context_data.csv')
    df['embedding'] = df['embedding'].apply(eval).apply(np.array)
    return df

df = load_data()

# Streamlit App
st.title("Question Answering with OpenAI Embeddings")

question = st.text_input("Enter your question:")
if st.button("Get Answer"):
    with st.spinner('Searching for the most relevant context...'):
        contexts = search_context(df, question, n=1)
        if contexts:
            with st.spinner('Generating the answer...'):
                answer = generate_answer(contexts[0], question)
                st.write("Answer:", answer)
        else:
            st.write("No relevant context found. Please try again with a different question.")

