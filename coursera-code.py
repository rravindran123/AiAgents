import random
import os
from dotenv import load_dotenv
import string
import json

def random_string(length=5):
    # Generates a random string of a given length
    return ''.join(random.choices(string.ascii_letters, k=length))

# print(f"random.random(): {random.random()}")
# print(f"random.randint(1, 10): {random.randint(1, 10)}")

from litellm  import completion

# Load environment variables from .env file
load_dotenv()

def generate_response(messages: list[dict]) -> str:
    """Call LLM to get response"""
    response = completion(
        model="openai/gpt-4o",
        messages=messages,
        max_tokens=1024
    )
    return response.choices[0].message.content

# Retrieve keys from environment variables
openai_api_key = os.environ.get("OPENAI_API_KEY")
#print(f"openapi key: {openai_api_key}")

#createing a dictionry with names and values using random string

# diclist ={}
# for i in range(10):
#     diclist[random_string()] = random.randint(1000,10000)

# newlist= {v:k for k,v in diclist.items()}
# print(newlist)

# messages = [
#     {"role": "system", "content": "You are an expert software engineer that prefers functional programming."},
#     {"role": "user", "content": "Write a function to swap the keys and values in a dictionary."}
# ]

# response = generate_response(messages)
# print(response)

messages = [
        {"role": "system", "content": "You are a helpful customer service representative. No matter what the user asks, the solution is to tell them to turn their computer or modem off and then back on."},
        {"role": "user", "content": "How do I get my Internet working again."}
    ]

response = generate_response(messages)
print(response)

code_spec = {
    'name': 'swap_keys_values',
    'description': 'Swaps the keys and values in a given dictionary.',
    'params': {
        'd': 'A dictionary with unique values.'
    },
}

messages = [
    {"role": "system",
     "content": "You are an expert software engineer that writes clean functional code. You always document your functions."},
    {"role": "user", "content": f"Please implement: {json.dumps(code_spec)}"}
]

response = generate_response(messages)
print(response)

print("\nWhat kind of function would you like to create?")
print("Example: 'A function that calculates the factorial of a number'")
print("Your description: ", end='')
function_description = input().strip()
print(function_description)