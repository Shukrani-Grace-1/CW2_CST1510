from openai import OpenAI
import streamlit as st



#accessing api key from secrets
api_key=st.secrets["OPENAI_API_KEY"]

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


print("ChatGPT Console Chat with memory")
print ("Type 'quit' to exit the program\n")

#initializing messages before the loop
messages=[
        {"role": "system", "content": "You are a helpful Python assistant."}
        ]

#loop to get questions from user
while True:
        user_input= input("Your question:")

        if user_input.lower()=="quit":
            print("Goodbye!")
            break

        #adding user messages in history        
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        #extracting the answer
        ai_answer= response.choices[0].message.content

        
        #adding the ai answer to the history
        messages.append({"role": "assistant", "content": ai_answer})


        #printing the ai answer
        print(f"\nAI answer:{ai_answer}")

