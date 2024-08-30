import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine
from openai import OpenAI

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def get_embedding(self, text, model="text-embedding-3-small"):
        """Generate an embedding for the input text."""
        response = openai.embeddings.create(
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

    def generate_text(self, prompt, model="gpt-4o-mini"):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            # Handle the response and potential errors
            if response and "choices" in response and len(response.choices) > 0:
                return response.choices[0].message.get('content', "No content available in the response.")
            else:
                error_details = f"Response: {response}\n"
                return f"Error: The response structure is not as expected. {error_details}"

        except openai.error.OpenAIError as e:
            # Catch and return any OpenAI API errors
            return f"OpenAI API Error: {str(e)}"
        except Exception as e:
            # Catch and return any other unexpected errors
            return f"Unexpected Error: {str(e)}"

    def generate_answer(self, context, question, model="gpt-4o-mini"):
        """Generate an answer using the most relevant context."""
        prompt = f"""Use the below context to answer the question. If the answer cannot be found, write 'I don't know.'

        Context:
        {context}

        Question: {question}
        """
        return self.generate_text(prompt, model=model)

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
