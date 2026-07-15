from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from dotenv import load_dotenv
import operator
import os

load_dotenv()

# ── State ─────────────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# ── Tools ─────────────────────────────────────────────────────
@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "chennai": "32C, sunny",
        "coimbatore": "30C, sunny",
        "erode": "31C, hot"
    }
    return weather_data.get(city.lower(), f"Weather data not available for {city}")

# ── LLM ───────────────────────────────────────────────────────
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

tools = [get_weather]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state:AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {
        "messages": [response]
    }

def tool_node(state:AgentState):
    last_message=state["messages"][-1]
    tool_results=[]

    for tool_call in last_message.tool_calls:
        if tool_call['name'] == 'get_weather':
            result = get_weather.invoke(tool_call["args"])
            tool_results.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"]
                )
            )
    
    return {
        "messages": tool_results
    }

def should_continue(state:AgentState):
    last_message=state["messages"][-1]

    if last_message.tool_calls:
        return "tools"
    return END


graph = StateGraph(AgentState)

graph.add_node('agent',agent_node)
graph.add_node('tools', tool_node)

# set entry point
graph.set_entry_point('agent')


graph.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END:END
    }
)

graph.add_edge("tools", "agent")

app = graph.compile()

results = app.invoke({
    "messages": [HumanMessage(content="What is the weather in chennai?")]
})

print("\nFinal answer:")
print(results["messages"][-1].content)