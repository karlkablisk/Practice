import os
import openai
import streamlit as st
import numpy as np
from scipy.spatial.distance import cosine
import tiktoken

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_embedding = "text-embedding-3-small"  # Use the small model as requested

    def get_embedding(self, text):
        """Generate an embedding for the input text."""
        response = self.client.embeddings.create(
            input=[text],
            model=self.model_embedding
        )
        embedding = response.data[0].embedding
        st.write(f"Embedding summary: Length = {len(embedding)}, First 5 values = {embedding[:5]}")
        return embedding

    def extract_metadata(self, text):
        """Extract metadata such as parts, chapters, sections, and page numbers from the text."""
        metadata = {}

        # Example regex-based extraction for parts, chapters, and pages
        lines = text.splitlines()
        for line in lines:
            if line.startswith("Part "):
                metadata['part'] = line.strip()
            elif line.startswith("Chapter "):
                metadata['chapter'] = line.strip()
            elif line.startswith("[start of page "):
                metadata['start_page'] = int(line.split(' ')[3].strip(']'))
            elif line.startswith("[end of page "):
                metadata['end_page'] = int(line.split(' ')[3].strip(']'))
            else:
                # Add other custom metadata extraction logic here
                pass

        return metadata

    def process_contexts(self, raw_contexts):
        """Process and embed each context with associated metadata."""
        contexts = []
        for context in raw_contexts:
            metadata = self.extract_metadata(context)
            embedding = self.get_embedding(context)
            contexts.append({
                "text": context,
                "embedding": embedding,
                "metadata": metadata
            })
        return contexts

    def search_context(self, contexts, query):
        """Search the most relevant context based on the cosine similarity of embeddings."""
        query_embedding = self.get_embedding(query)
        similarities = [
            1 - cosine(np.array(context['embedding']), np.array(query_embedding))
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
        metadata_info = " ".join([f"{key}: {value}" for key, value in context['metadata'].items()])
        prompt = f"""Use the below context and metadata to answer the question. If the answer cannot be found, write 'I don't know.'

        Metadata:
        {metadata_info}

        Context:
        {context['text']}

        Question: {question}
        """
        return self.generate_text(prompt, model=model)

    def run(self):
        st.title("Question Answering with OpenAI Embeddings and Metadata")

        text_input = st.text_area("Text Contexts", height=200)
        raw_contexts = text_input.split("\n\n")

        # Process and embed each context with metadata
        contexts = self.process_contexts(raw_contexts)

        question = st.text_input("Enter your question:")

        if st.button("Get Answer"):
            if contexts and question:
                with st.spinner('Searching for the most relevant context...'):
                    best_context = self.search_context(contexts, question)
                    with st.spinner('Generating the answer...'):
                        answer = self.generate_answer(best_context, question)
                        if answer:
                            st.write("Answer:", answer)
                            st.write("Metadata:", best_context['metadata'])
            else:
                st.write("Please provide both contexts and a question.")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
