import os, subprocess
from dotenv import load_dotenv
from anthropic import Anthropic

TOOLS = [
    {
        "name": "bash",
        "description": "Run a shell command",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string"
                }
            },
            "required": ["command"]
        }
    }
]

def run_command(command):

    try: 
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        out = (result.stdout + result.stderr).strip()
        return out if out else "(no output)"

    except subprocess.TimeoutExpired:
        return "Error: Timeout (30s)"



def agent_loop(messages, client, model, system = ""):

    while True:

        response = client.messages.create(
            model = model,
            max_tokens = 1000,
            tools = TOOLS,
            messages = messages,
            system = system,
        )

        messages.append(
            {
                "role": "assistant",
                "content": response.content,
            }
        )

        if response.stop_reason != "tool_use":
            return
        
        else: 
            results = []

            for block in response.content:

                if block.type == "tool_use":
                    output = run_command(block.input["command"])
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                        })

            messages.append({
                "role": "user",
                "content": results,
            })


if __name__ == "__main__":

    load_dotenv()

    client = Anthropic()

    model = os.environ.get("MODEL_ID")

    system = "Give a short and concise answer to the user's query."

    messages = []

    while True:

        query = input("\nEnter a query: ")

        if query.lower() == "exit" or query.lower() == "quit" or query.lower() == "q":
            break

        else:
            messages.append(
                {
                    "role": "user",
                    "content": query
                }
            )

            agent_loop(messages, client, model, system)

            blocks = messages[-1]["content"]

            for block in blocks:
                if getattr(block, "type", None) == "text":
                    print(block.text)