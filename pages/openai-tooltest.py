import os
import streamlit as st
from openai import OpenAI

# Models for text generation
gpt35 = "gpt-3.5-turbo"
gpt4t = "gpt-4-turbo"
gpto = "gpt-4o"
gptop = "gpt-4o-2024-08-06"
gptomini = "gpt-4o-mini"

class OpenAIStreamlitApp:
    def __init__(self):
        # Initialize the OpenAI client with the API key from the environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Define the assistant with a tool to get the quantity of a specific fruit
        self.assistant = self.client.beta.assistants.create(
            instructions="You are an assistant that can provide the quantity of specific fruits using a tool.",
            model="gpt-4o-2024-08-06",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_fruit_quantity",
                        "description": "Get the quantity of a specific fruit",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "fruit": {
                                    "type": "string",
                                    "description": "The name of the fruit, e.g., apple, pear"
                                }
                            },
                            "required": ["fruit"]
                        }
                    }
                }
            ]
        )

        # Define a simple fruit quantity mapping
        self.fruit_quantities = {
            "apple": 128,
            "pear": 66,
            "banana": 75,
            "orange": 45
        }

    def generate_text(self, prompt, model):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        message_content = response.choices[0].message.content

        # Check if the AI's response indicates it needs to use the fruit tool
        if "apple" in prompt.lower() or "pear" in prompt.lower() or "banana" in prompt.lower() or "orange" in prompt.lower():
            fruit = self.extract_fruit(prompt)
            if fruit:
                st.warning("Fruit tool used")
                quantity = self.get_fruit_quantity(fruit)
                return f"There are {quantity} {fruit}s."
            else:
                return message_content
        else:
            return message_content

    def extract_fruit(self, prompt):
        """Simple extraction of a fruit name from the prompt."""
        fruits = ["apple", "pear", "banana", "orange"]
        for fruit in fruits:
            if fruit in prompt.lower():
                return fruit
        return None

    def get_fruit_quantity(self, fruit):
        """Uses the assistant's tool to get the quantity of a specific fruit."""
        return self.fruit_quantities.get(fruit.lower(), "Unknown")

    def run(self):
        st.title('Text Generator and Fruit Quantity Assistant')

        # Dropdown for model selection with gpt-4o as the default
        model_choice = st.selectbox(
            "Choose GPT Model:", 
            [gpt35, gpt4t, gpto, gptop, gptomini],
            index=2  # Setting gpt-4o as the default
        )

        prompt_text = st.text_area("Enter your prompt:")
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

        # Manual input method to test the fruit quantity tool
        fruit = st.text_input("Enter a fruit name to get its quantity:")
        if st.button("Get Fruit Quantity"):
            if not fruit.strip():
                st.error("Please enter a fruit name.")
            else:
                try:
                    quantity = self.get_fruit_quantity(fruit)
                    st.text_area("Retrieved Quantity:", value=f"{quantity}", height=50)
                    st.success("Fruit quantity retrieved successfully.")
                except Exception as e:
                    st.error(f"Error retrieving fruit quantity: {e}")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
