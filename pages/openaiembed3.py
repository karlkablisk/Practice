import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine
from openai import OpenAI
import tiktoken  # For token count

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
        embedding = response.data[0].embedding
        st.write(f"Embedding summary: Length = {len(embedding)}, First 5 values = {embedding[:5]}")
        return embedding

    def search_context(self, contexts, query, model="text-embedding-3-small"):
        """Search the most relevant context based on the cosine similarity of embeddings."""
        query_embedding = self.get_embedding(query, model=model)
        similarities = [
            1 - cosine(np.array(self.get_embedding(context, model=model)), np.array(query_embedding))
            for context in contexts
        ]
        top_index = np.argmax(similarities)
        return contexts[top_index]

    def count_tokens(self, text, model="gpt-4o-mini"):
        """Count the number of tokens in the given text."""
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))

    def generate_text(self, prompt, model="gpt-4o-mini", max_tokens=1500):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        try:
            total_tokens = self.count_tokens(prompt, model=model) + max_tokens
            if total_tokens > 8192:  # Example limit, adjust based on your model
                raise ValueError(f"Total token count exceeds the model's limit: {total_tokens} tokens")

            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        except openai.error.OpenAIError as e:
            st.error(f"OpenAI API Error: {str(e)}")
        except Exception as e:
            st.error(f"Error generating text: {str(e)}")

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

        # Add a dropdown to select the GPT model
        model = st.selectbox(
            "Select GPT Model:",
            options=["gpt-4-turbo", "gpt-4o", "gpt-4o-mini"],
            index=2  # Default to "gpt-4o-mini"
        )

        text_input = st.text_area("Text Contexts", height=200)
        contexts = text_input.split("\n\n")

        question = st.text_input("Enter your question:")

        if st.button("Get Answer"):
            if contexts and question:
                with st.spinner('Searching for the most relevant context...'):
                    best_context = self.search_context(contexts, question, model=model)
                    with st.spinner('Generating the answer...'):
                        answer = self.generate_answer(best_context, question, model=model)
                        if answer:
                            st.write("Answer:", answer)
            else:
                st.write("Please provide both contexts and a question.")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
