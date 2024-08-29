import os
import streamlit as st
import json
import pandas as pd
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from pydantic import BaseModel, Field
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema import StrOutputParser

# Load environment variables
load_dotenv()

# Define the GPT models
gpt35 = "gpt-3.5-turbo"
gpt4t = "gpt-4-turbo"
gpto = "gpt-4o"
gptomini = "gpt-4o-mini"

# Set the default model
default_model = gptomini

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = ChatOpenAI(model_name=default_model, temperature=0)

    def generate_text(self, prompt):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.completions.create(
            model=default_model,
            messages=messages,
            max_tokens=150
        )
        return response.choices[0].message.content

def process_and_classify_document(filename):
    loader = PyPDFLoader(filename)
    pages = loader.load_and_split()

    ids = [str(i) for i in range(1, len(pages) + 1)]

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(pages, embeddings, ids=ids)
    retriever = vectordb.as_retriever()

    schema = ScienceDirectDocument.model_json_schema()

    template = """Use the following pieces of context to accurately classify the documents based on the schema passed. Output should follow the pattern defined in schema.
    No verbose should be present. Output should follow the pattern defined in schema and the output should be in json format only so that it can be directly used with json.loads():
    {context}
    schema: {schema}
    """
    rag_prompt_custom = PromptTemplate.from_template(template)
    llm = ChatOpenAI(model_name=default_model, temperature=0)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "schema": RunnablePassthrough()}
        | rag_prompt_custom
        | llm
        | StrOutputParser()
    )
    output = json.loads(rag_chain.invoke(str(schema)))
    vectordb._collection.delete(ids=[ids[-1]])
    return output

def send_request(fileobj):
    json_output = process_and_classify_document(filename=fileobj)
    table_output = pd.DataFrame(list(json_output.items()), columns=['Key', 'Value'])
    return json_output, table_output

def main():
    st.title("PDF Metadata Extractor using RAG")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file is not None:
        with open(f"temp_{uploaded_file.name}", 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        st.write(f"Processing file: {uploaded_file.name}")
        
        json_output, table_output = send_request(f"temp_{uploaded_file.name}")
        
        st.subheader("JSON Output")
        st.json(json_output)
        
        st.subheader("Table Output")
        st.dataframe(table_output)

        st.subheader("Ask a Question")
        user_question = st.text_input("Enter your question about the document:")
        
        if user_question:
            app = OpenAIStreamlitApp()
            generated_answer = app.generate_text(user_question)
            st.subheader("Generated Answer")
            st.write(generated_answer)

if __name__ == "__main__":
    main()
