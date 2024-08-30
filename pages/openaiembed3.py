import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize OpenAI client
        self.client = openai

    def get_embedding(self, text, model="text-embedding-3-small"):
        """Generate an embedding for the input text."""
        response = self.client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding

    def search_context(self, contexts, query, model="text-embedding-3-small"):
        """Search the most relevant context based on the cosine similarity of embeddings."""
        query_embedding = self.get_embedding(query, model=model)
        similarities = [
            1 - cosine(np.array(self.get_embedding(context, model=model)), np.array(query_embedding))
            for context in contexts
        ]
        top_index = np.argmax(similarities)
        return contexts[top_index]

    def generate_answer(self, context, question, model="gpt-4o-mini"):
        """Generate an answer using the most relevant context."""
        prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

        Context:
        {context}

        Question: {question}
        """
        response = self.client.chat_completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0
        )
        return response.choices[0].message['content']

    def run(self):
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
                    best_context = self.search_context(contexts, question)
                    with st.spinner('Generating the answer...'):
                        answer = self.generate_answer(best_context, question)
                        st.write("Answer:", answer)
            else:
                st.write("Please provide both contexts and a question.")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
