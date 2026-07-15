from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
import operator
import os


load_dotenv()


class AgentState(TypedDict):
    messages: Annotated[list, operator.add]


llm = ChatGroq(
    temperature=0,
    model_name="llama-3.3-70b-versatile",
    groq_api_key=os.getenv("GROQ_API_KEY"),
)


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    weather_data = {
        "chennai": "32C, sunny",
        "coimbatore": "30C, sunny",
        "erode": "31C, hot",
    }

    return weather_data.get(city.lower(), f"Weather Data not found for {city}")


@tool
def calculator(experssion: str) -> str:
    """Calculates the given expersion example: '20*5' or '100/5'"""
    try:
        result = eval(experssion)
        return f"{experssion} = {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def get_current_time(city: str) -> str:
    """Get the current time for a city."""
    times = {
        "chennai": "IST 10:30 AM",
        "london": "GMT 5:00 AM",
        "new york": "EST 12:00 AM",
    }

    return times.get(city.lower(), f"Time Data not found for {city}")


tools = [get_weather, calculator, get_current_time]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: AgentState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools)


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END


from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")

graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})

graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "user_1"}}


print("===========Conversation with memory===============")

result = app.invoke(
    {"messages": [HumanMessage(content="What's the weather in chennai?")]},
    config=config,
)

print(f"Q: What is the weather in Chennai?")
print(f"A: {result['messages'][-1].content}\n")

# message 2 — refers to previous context
result = app.invoke(
    {"messages": [HumanMessage(content="What time is it there?")]},
    config=config  # ← same thread_id = same conversation
)
print(f"Q: What time is it there?")
print(f"A: {result['messages'][-1].content}\n")

# message 3
result = app.invoke(
    {"messages": [HumanMessage(content="What is 100 / 4?")]},
    config=config
)
print(f"Q: What is 100 / 4?")
print(f"A: {result['messages'][-1].content}\n")

# message 4 — test different thread (no memory of Chennai)
config2 = {"configurable": {"thread_id": "user_2"}}
result = app.invoke(
    {"messages": [HumanMessage(content="What time is it there?")]},
    config=config2  # ← different thread_id = fresh conversation
)
print(f"=== New conversation (user_2) ===")
print(f"Q: What time is it there?")
print(f"A: {result['messages'][-1].content}")
