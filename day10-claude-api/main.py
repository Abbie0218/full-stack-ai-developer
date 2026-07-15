from groq import Groq
import os
from dotenv import load_dotenv
from ai_client import extract_text, client, ask_with_retry


load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")


def ask(question: str, model: str = DEFAULT_MODEL):
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": question}], max_tokens=500
    )
    return extract_text(response)


def multi_turn_chat(model: str = DEFAULT_MODEL):
    messages = []

    print(f"Hello,I'm your Ai Assistant...How may I help you?")
    print(f"Type quit to end session")

    while True:
        user_input = input("You: ")

        if user_input.lower() == "quit":
            break
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":user_input}]
        )
        
        assistant_message = extract_text(response)
        print(f"AI:{assistant_message}\n")

        messages.append({"role":"assistant", "content":assistant_message})

# temperature usage
# question = "Invent a funny name for a Python web framework"

# print("=== Temperature 0 ===")
# for i in range(3):
#     response = client.chat.completions.create(
#         model=DEFAULT_MODEL,
#         messages=[{"role": "user", "content": question}],
#         temperature=0,
#         max_tokens=20
#     )
#     print(f"Run {i+1}: {extract_text(response)}")

# print("\n=== Temperature 1.0 ===")
# for i in range(3):
#     response = client.chat.completions.create(
#         model=DEFAULT_MODEL,
#         messages=[{"role": "user", "content": question}],
#         temperature=1.0,
#         max_tokens=20
#     )
#     print(f"Run {i+1}: {extract_text(response)}")

# system prompt

# def ask_with_system_prompt(model:str=DEFAULT_MODEL):
    
#     print(f"I'm here to assist you..How may I help you?")
#     print(f"To end session, pls type quit")

#     system_prompt = "You are a 5 year old child. Use simple words only."
#     messages=[]
    
#     while True:
#         user_input = input("You: ")
        
#         if user_input.lower() == 'quit':
#             print(f"Bye Bye...")
#             break
#         messages.append({"role":"user","content":user_input})

#         response = client.chat.completions.create(
#             model=model,
#             messages=[
#                 {"role":"system","content":system_prompt},
#                 *messages
#             ])
        
#         assistant_message = extract_text(response)
#         print(f"AI:{assistant_message}")

#         messages.append({"role":"assistant","content":assistant_message})
        

# ask_with_system_prompt()



result = ask_with_retry("What is Python in one sentence?")
print(result)
