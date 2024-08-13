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

        # Define the assistant with a tool to get the current temperature
        self.assistant = self.client.beta.assistants.create(
            instructions="You are an assistant that can provide the current temperature using a tool.",
            model="gpt-4o-2024-08-06",
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_current_temperature",
                        "description": "Get the current temperature for a specific location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g., San Francisco, CA"
                                },
                                "unit": {
                                    "type": "string",
                                    "enum": ["Celsius", "Fahrenheit"],
                                    "description": "The temperature unit to use."
                                }
                            },
                            "required": ["location", "unit"]
                        }
                    }
                }
            ]
        )

    def generate_text(self, prompt, model):
        """Uses the specified GPT model to generate a response based on the input prompt."""
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

        message_content = response.choices[0].message.content

        # Check if the AI's response indicates it needs to use the temperature tool
        if "weather" in prompt.lower() or "temperature" in prompt.lower():
            location = self.extract_location(prompt)
            if location:
                temperature = self.get_temperature(location)
                return f"The current temperature in {location} is {temperature} degrees."
            else:
                return message_content
        else:
            return message_content

    def extract_location(self, prompt):
        """Simple extraction of a location from the prompt."""
        # In a real application, you would use a more sophisticated method to extract the location.
        # Here, we'll just look for a keyword like "in" and take the next word.
        words = prompt.split()
        if "in" in words:
            index = words.index("in")
            if index + 1 < len(words):
                return words[index + 1]
        return None

    def get_temperature(self, location, unit="Celsius"):
        """Uses the assistant's tool to get the current temperature for a location."""
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"What is the current temperature in {location} in {unit}?"
        )

        # Start the run and handle tool invocation
        temperature = "Unknown"
        with self.client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=self.assistant.id
        ) as stream:
            for event in stream.text_deltas:
                if event.get('event') == 'thread.run.requires_action':
                    tool_calls = event['data']['required_action']['submit_tool_outputs']['tool_calls']
                    for tool_call in tool_calls:
                        if tool_call['function']['name'] == 'get_current_temperature':
                            tool_call_id = tool_call['id']
                            # Simulate returning the temperature, e.g., "25" degrees
                            tool_output = {"tool_call_id": tool_call_id, "output": "25"}
                            stream.submit_tool_outputs([tool_output], event['data']['id'])
                if 'text' in event:
                    temperature = event['text']

        return temperature

    def run(self):
        st.title('Text Generator and Temperature Assistant')

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

        # Get temperature for a location using the assistant tool manually
        location = st.text_input("Enter a location to get the temperature:")
        unit = st.selectbox("Select unit", ["Celsius", "Fahrenheit"], index=0)
        if st.button("Get Temperature"):
            if not location.strip():
                st.error("Please enter a location.")
            else:
                try:
                    temperature = self.get_temperature(location, unit)
                    st.text_area("Retrieved Temperature:", value=temperature, height=50)
                    st.success("Temperature retrieved successfully.")
                except Exception as e:
                    st.error(f"Error retrieving temperature: {e}")

if __name__ == "__main__":
    app = OpenAIStreamlitApp()
    app.run()
