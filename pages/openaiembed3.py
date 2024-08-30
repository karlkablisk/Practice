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
        embedding = response.data[0].embedding
        # Output embedding summary
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

    def generate_text(self, prompt, model="gpt-4o-mini"):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            
            # Extract and return the message content
            if response and "choices" in response and len(response.choices) > 0:
                # Extract the content
                message_content = response.choices[0].message.content
                # Display detailed response info in a warning
                st.warning(f"Response Details:\n{response}")
                return message_content
            else:
                error_details = f"Response: {response}\n"
                st.warning(error_details)
                return "Error: The response structure is not as expected."

        except openai.error.OpenAIError as e:
            # Catch and return any OpenAI API errors
            st.warning(f"OpenAI API Error: {str(e)}")
            return f"OpenAI API Error: {str(e)}"
        except Exception as e:
            # Catch and return any other unexpected errors
            st.warning(f"Unexpected Error: {str(e)}")
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
