from tools import get_weather, calculate, search_notes, TOOLS
from ai_client import client
import os
from dotenv import load_dotenv
import json
load_dotenv()

TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_notes": search_notes
}

def run_agent(user_message:str):
    messages=[{"role":"user","content":user_message}]
    max_iterations=10
    iteration=0

    while iteration < max_iterations:
        iteration+=1
        print(f"Iteration {iteration} Begins...")
        response = client.chat.completions.create(
            model = os.getenv("SMART_MODEL"),
            tools=TOOLS,
            tool_choice="auto",
            messages=messages
        )
        message=response.choices[0].message
        # print(f"tool_calls:",message.tool_calls)
        # print(f"content:",message.content)
        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                tool_name=tool_call.function.name
                tool_args=json.loads(tool_call.function.arguments)
                print(f"Running {tool_name}({tool_args})")
                result=TOOL_MAP[tool_name](**tool_args)
                print(f"Result:{result}")
                messages.append({
                    "role":"tool",
                    "tool_call_id":tool_call.id,
                    "content":json.dumps(result)
                })
        else:
            print(f"\nFinal: {message.content}")
            return message.content
    return "Max iterations reached"

run_agent("What is 15 * 47 + 23?")
run_agent("What is the weather in chennai?")
run_agent("Search my notes for meeting")