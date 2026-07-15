from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = os.getenv("DEFAULT_MODEL", "llama-3.1-8b-instant")

# ── Tools ─────────────────────────────────────────────────────
def calculator(expression: str) -> str:
    expression = expression.replace(",", "")  # ✅ remove commas
    try:
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"

def get_current_date() -> str:
    from datetime import date
    return str(date.today())

def search_wikipedia(query: str) -> str:
    # mock for now
    wiki_data = {
        "python programming language": "Python was created by Guido van Rossum and released in 1991.",
        "chennai population": "Chennai has a population of approximately 7.1 million (2023).",
        "india population": "India has a population of approximately 1.4 billion (2023)."
    }
    for key in wiki_data:
        if query.lower() in key:
            return wiki_data[key]
    return f"No Wikipedia data found for: {query}"

# ── Tool map ──────────────────────────────────────────────────
TOOLS = {
    "calculator": calculator,
    "get_current_date": get_current_date,
    "search_wikipedia": search_wikipedia
}

# ── Tool definitions for LLM ──────────────────────────────────
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression e.g. '1400000 * 0.03'"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's date",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information about a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Topic to search"}
                },
                "required": ["query"]
            }
        }
    }
]


# ── ReAct loop ────────────────────────────────────────────────
def run_agent(user_question: str, max_iterations: int = 5) -> str:
    print(f"\n{'='*50}")
    print(f"Question: {user_question}")
    print(f"{'='*50}")

    messages = [{
            "role": "system",
            "content": """You are a helpful assistant. 
For questions about facts/data → ALWAYS use search_wikipedia first.
For date calculations → ALWAYS use get_current_date first.
For math → use calculator.
Never guess numbers — always look them up."""
        },
        {"role": "user", "content": user_question}
    ]
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        # ── LLM call ──────────────────────────────────────────
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        # ── THOUGHT ───────────────────────────────────────────
        if message.content:
            print(f"THOUGHT: {message.content}")

        # ── No tool calls = final answer ──────────────────────
        if not message.tool_calls:
            print(f"\nFINAL ANSWER: {message.content}")
            return message.content

        # ── ACTION ────────────────────────────────────────────
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # run each tool call
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            print(f"ACTION: {tool_name}({tool_args})")

            # ── OBSERVATION ───────────────────────────────────
            tool_fn = TOOLS.get(tool_name)
            if tool_fn:
                if tool_args and len(tool_args) > 0:
                    result = tool_fn(**tool_args)
                else:
                    result = tool_fn()
            else:
                result = f"Tool {tool_name} not found"

            print(f"OBSERVATION: {result}")

            # add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    return "Max iterations reached — could not complete task"


# ── Test ──────────────────────────────────────────────────────
questions = [
    "What is Chennai population multiplied by 0.03?",
    "How many years since Python was created?",
]

for q in questions:
    run_agent(q)