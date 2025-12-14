from openai import OpenAI; from dotenv import load_dotenv; import os

load_dotenv(); client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


print("ChatGPT Console Chat")
print ("Type 'quit' to exit the program\n")

#loop to get questions from user
while True:
    user_input= input("Your question:")

    if user_input.lower()=="quit":
        print("Goodbye!")
        break

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful Python assistant."},
            {"role": "user", "content": user_input}]
    )

#printing the answer
    answer= response.choices[0].message.content
    print(f"\nAI answer:{answer}")

