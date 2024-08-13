import os
import streamlit as st
from openai import OpenAI

# Load OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# Models for text generation
gpt35 = "gpt-3.5-turbo"
gpt4t = "gpt-4-turbo"
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

class OpenAIStreamlitApp:
    def generate_text(self, prompt, model):
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content

    def run(self):
        st.title("OpenAI Text Generation")

        # Dropdown for model selection with gpt4op as the default
        model_choice = st.selectbox(
            "Choose GPT Model:", 
            [gpt35, gpt4t, gpto, gptop, gptomini],
            index=[gpt35, gpt4t, gpto, gptop, gptomini].index(gptop)  # Setting gpt4op as the default
        )

        prompt_text = st.text_area("Enter your prompt:", value="Hello, what's on your mind today?")

        if st.button("Generate Text"):
            if not prompt_text.strip():
                st.error("Please enter some prompt text.")
            else:
                try:
                    generated_text = self.generate_text(prompt_text, model_choice)
                    st.text_area("Generated Text:", value=generated_text, height=300)
                    st.success("Text generated successfully.")
                except Exception as e:
                    st.error(f"Error generating text: {e}")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
