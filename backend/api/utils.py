# import openai
# import base64
# openai.api_key = "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"  # Replace with your actual API key

# def encode_image(image_file):
#     """
#     Encodes an uploaded image file as a base64 string.
#     """
#     return base64.b64encode(image_file.read()).decode("utf-8")


# def generate_chemistry_response(conversation):
#     """
#     Generate a response from OpenAI's chat completion API based on the given conversation history.
#     """
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": "You are a highly specialized assistant focused exclusively on A and O Level Chemistry. "
#                "Your behavior is as follows: "
#                "- If the user greets you (e.g., 'Hello', 'Hi', 'Good morning'), respond with a short, polite greeting, such as: "
#                "  'Hello! How can I assist you with Chemistry today?' "
#                "- If the user asks a question unrelated to Chemistry, respond politely but firmly with: "
#                "  'I can only assist with chemistry-related questions. Please ask something related to Chemistry.' "
#                "Be concise and stay strictly within the scope of A and O Level Chemistry."},
#                 *conversation,  # Pass the full conversation history
#             ]
#         )
#         return response["choices"][0]["message"]["content"].strip()
#     except Exception as e:
#         return f"Error generating response: {str(e)}"
import openai
import base64
import json

# Load API key and model from the configuration file
import os

def load_config():
    config_path = os.path.join(os.getcwd(),"api", "config", "config.json")  # Dynamically generate the path
    with open(config_path, "r") as f:
        config = json.load(f)
    return config

# Set up OpenAI API key from the config file
config = load_config()
openai.api_key = config["openai_api_key"]

def encode_image(image_file):
    """
    Encodes an uploaded image file as a base64 string.
    """
    return base64.b64encode(image_file.read()).decode("utf-8")

def generate_chemistry_response(conversation):
    """
    Generate a response from OpenAI's chat completion API based on the given conversation history.
    """
    try:
        response = openai.ChatCompletion.create(
            model=config["model"],  # Use model from config file
            messages=[
                {"role": "system", "content": "You are a highly specialized assistant focused exclusively on A and O Level Chemistry. "
               "Your behavior is as follows: "
               "- If the user greets you (e.g., 'Hello', 'Hi', 'Good morning'), respond with a short, polite greeting, such as: "
               "  'Hello! How can I assist you with Chemistry today?' "
               "- If the user asks a question unrelated to Chemistry, respond politely but firmly with: "
               "  'I can only assist with chemistry-related questions. Please ask something related to Chemistry.' "
               "Be concise and stay strictly within the scope of A and O Level Chemistry."},
                *conversation,  # Pass the full conversation history
            ]
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
