import random
import os
from dotenv import load_dotenv
import string
import json
from litellm import completion
from typing import List, Dict
import sys

agent_rules = [{
    "role": "system",
    "content": """
You are an AI agent that can perform tasks by using available tools.

Available tools:

```json
{
    "list_files": {
        "description": "Lists all files in the current directory.",
        "parameters": {}
    },
    "read_file": {
        "description": "Reads the content of a file.",
        "parameters": {
            "file_name": {
                "type": "string",
                "description": "The name of the file to read."
            }
        }
    },
    "terminate": {
        "description": "Ends the agent loop and provides a summary of the task.",
        "parameters": {
            "message": {
                "type": "string",
                "description": "Summary message to return to the user."
            }
        }
    }
}
```

If a user asks about files, documents, or content, first list the files before reading them.

When you are done, terminate the conversation by using the "terminate" tool and I will provide the results to the user.

Important!!! Every response MUST have an action.
You must ALWAYS respond in this format:

<Stop and think step by step. Parameters map to args. Insert a rich description of your step by step thoughts here.>

```action
{
    "tool_name": "insert tool_name",
    "args": {...fill in any required arguments here...}
}
```"""
}]

def list_files() -> list:
    """
    Lists all files in the current directory.
    Returns:
        List[str]: A list of file names (strings) in the current directory.
    """
    # List everything in the current directory.
    # You can filter out directories if you wish:
    return [f for f in os.listdir('.') if os.path.isfile(f)]

def read_file(file_name: str) -> str:
    """
    Reads the contents of a file.
    
    Args:
        file_name (str): The name of the file to read.
        
    Returns:
        str: The content of the file.
    """
    try:
        with open(file_name, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file '{file_name}': {e}"

def generate_response(messages: List[Dict]) -> str:
   """Call LLM to get response"""
   response = completion(
      model="openai/gpt-4",
      messages=messages,
      max_tokens=1024
   )
   return response.choices[0].message.content

def extract_markdown_block(response: str, block_name: str) -> str:
    """Extract code from response 

    ```action
{
    "tool_name": "insert tool_name",
    "args": {...fill in any required arguments here...}
}
  """
    if not '```' in response:
        print("No code block found")
        return response
    code_block = response.split('```')[1].strip()
    
    if code_block.startswith("action"):
        code_block=code_block[6:]

    return code_block


def parse_action(response: str) -> Dict:
    """Parse the LLM response into a structured action dictionary."""
    try:
        response = extract_markdown_block(response, "action")
        response_json = json.loads(response)
        print("response_json",response_json)
        if "tool_name" in response_json and "args" in response_json:
            return response_json
        else:
            return {"tool_name": "error", "args": {"message": "You must respond with a JSON tool invocation."}}
    except json.JSONDecodeError:
        #return {"tool_name": "error", "args": {"message": "Invalid JSON response. You must respond with a JSON tool invocation."}}
        return {"tool_name": "say", "args": {"message": response}}

def agent_loop(max_iteration:int):

    iterations=0
    memory=[]

    while iterations < max_iteration:

        # 1. Construct prompt: Combine agent rules with memory
        prompt = agent_rules + memory

        # 2. Generate response from LLM
        print("Agent thinking...")
        response = generate_response(prompt)
        print(f"Agent response: {response}")

        # 3. Parse response to determine action
        action = parse_action(response)

        result = "Action executed"

        if action["tool_name"] == "list_files":
            result = {"result":list_files()}
        elif action["tool_name"] == "read_file":
            result = {"result":read_file(action["args"]["file_name"])}
        elif action["tool_name"] == "error":
            result = {"error":action["args"]["message"]}
        elif action["tool_name"] == "terminate":
            print(action["args"]["message"])
            break
        else:
            result = {"error":"Unknown action: "+action["tool_name"]}

        print(f"Action result: {result}")

        # 5. Update memory with response and results
        memory.extend([
            {"role": "assistant", "content": response},
            {"role": "user", "content": json.dumps(result)}
        ])

        # 6. Check termination condition
        if action["tool_name"] == "terminate":
            break

        iterations += 1

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Retrieve keys from environment variables
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key is None:
        print("Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)

    agent_loop(5)

if __name__ == "__main__":
    main()