import streamlit as st

from openai import OpenAI
import os

#load api key from environement variable
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

#context aware prompt

messages = [
    {"role": "system", "content": "You are a helpful Python assistant."},
    {"role": "user", "content": "Write an explanation of API for beginners."}
]

#call openAi API

response = client.chat.completions.create(
    model="gpt-4o",
    messages= messages
)

#print the response
print(response.choices[0].message.content)
