from typing import TypedDict, Annotated
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, StateGraph
from langchain_core.messages import HumanMessage
import operator
import os

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

llm = ChatGroq(
    groq_api_key=os.getenv('GROQ_API_KEY'),
    temperature=0,
    model_name="llama-3.3-70b-versatile"
)

@tool
def get_weather_data(city:str)->str:
    """get current weather for the city"""
    weather_data = {
        "chennai": "32C, sunny",
        "coimbatore": "30C, sunny",
        "bangalore": "25C, cloudy",
        "mumbai": "30C, humid"
    }
    return weather_data.get(city.lower(),f"No weather data found for {city}")


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

tools = [get_current_time, calculator, get_weather_data]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state:AgentState):
    response= llm_with_tools.invoke(state["messages"])
    return {
        "messages" : [response]
    }

tool_node=ToolNode(tools)

def should_continue(state:AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    else:
        return END


from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

graph = StateGraph(AgentState)

graph.add_node('agent', agent_node)
graph.add_node('tools',tool_node)

graph.set_entry_point('agent')

graph.add_conditional_edges('agent', should_continue, {"tools": "tools", END: END})

graph.add_edge("tools", "agent")

app = graph.compile(checkpointer=memory)

def run_agent(message:str, thread_id:int)->dict:
    config = {"configurable": {"thread_id": thread_id}}
    result = app.invoke(
        {
            "messages" : [HumanMessage(content=message)]
        },
        config=config
    )

    tool_used=[]

    for msg in result['messages']:
        if hasattr(msg,'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_used.append(tc['name'])
    
    return{
        'answer': result['messages'][-1].content,
        "tools_used": tool_used
    }