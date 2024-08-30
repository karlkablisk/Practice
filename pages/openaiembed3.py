import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize OpenAI client with environment variable
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(self, text, model="gpt-4o-mini"):
        """Uses the specified GPT model to generate an embedding for the input text."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Generate an embedding for the following text."},
                {"role": "user", "content": text}
            ],
            functions=[{
                "name": "embeddings.create",
                "description": "Generate embeddings for the provided text.",
                "parameters": {
                    "model": "text-embedding-3-small",
                    "input": [text]
                }
            }],
            function_call="auto"
        )
        return response.choices[0].message["function_call"]["arguments"]["embedding"]

    def search_context(self, contexts, query, model="gpt-4o-mini"):
        """Searches the most relevant context based on the cosine similarity of embeddings."""
        query_embedding = self.get_embedding(query, model=model)
        similarities = [
            1 - cosine(np.array(self.get_embedding(context, model=model)), np.array(query_embedding))
            for context in contexts
        ]
        top_index = np.argmax(similarities)
        return contexts[top_index]

    def generate_answer(self, context, question, model="gpt-4o-mini"):
        """Generates an answer using the most relevant context and the specified GPT model."""
        prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

        Context:
        {context}

        Question: {question}
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant."},
                      {"role": "user", "content": prompt}],
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

