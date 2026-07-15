from typing import TypedDict, Annotated
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
import os
import operator
import sqlite3
import time


load_dotenv()

llm = ChatGroq(
    groq_api_key = os.getenv('GROQ_API_KEY'),
    temperature=0,
    model_name="llama-3.3-70b-versatile"
)

class AgentState(TypedDict):
        messages:Annotated[list, operator.add]

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


def summarize_messages(messages:list) -> list:
    if len(messages) <= 20:
        return messages

    to_summarize = messages[:-4]
    recent =  messages[-4:]


    conversation = ""
    for msg in to_summarize:
        role = msg.__class__.__name__.replace("Message","")
        content = msg.content if hasattr(msg,'content') else ""

        if content:
            conversation +=  f"{role}: {content}\n"
    
    summary_response = llm.invoke([
        SystemMessage(content="Summarize this conversation in 2-3 sentence"),
        HumanMessage(content=conversation)
    ])

    summary = SystemMessage(
        content=f"Previous Conversation summary: {summary_response.content}"
    )

    print(f"📝 Summarized {len(to_summarize)} messages → 1 summary")
    return [summary] + recent

def agent_node(state: AgentState):
    # summarize only for LLM context — don't save back to state
    messages_for_llm = summarize_messages(state["messages"])
    response = llm_with_tools.invoke(messages_for_llm)
    return {"messages": [response]}  # only add AI response to state


tool_node = ToolNode(tools)

def should_continue(state:AgentState):
    last_message=state['messages'][-1]
    if last_message.tool_calls:
        return "tools"
    return END

conn = sqlite3.connect("memory.db",check_same_thread=False)
graph = StateGraph(AgentState)

graph.add_node('agent',agent_node)
graph.add_node('tools',tool_node)
graph.set_entry_point('agent')
graph.add_conditional_edges('agent',should_continue,{"tools":"tools", END: END})
graph.add_edge('tools','agent')
memory=SqliteSaver(conn)
app = graph.compile(checkpointer=memory)

def run_agent(message:str, thread_id:str)->dict:
    config={'configurable':{'thread_id':thread_id}}
    result= app.invoke(
        {
            "messages": [HumanMessage(content=message)]
        },
        config=config
    )

    return{
        "answer": result['messages'][-1].content,
        "message_count": len(result["messages"])
    }

if __name__ == "__main__":
    thread_id = f"test_{int(time.time())}"
    print(f"Thread ID   : {thread_id}")
    questions = [
        "What is the weather in Chennai?",
        "What about Bangalore?",
        "What is 100 * 5?",
        "What is the weather in Mumbai?",
        "What about Coimbatore?",
        "What is 200 / 4?",
        "What was the first city I asked about?",  # tests summarization
    ]

    for q in questions:
        print(f"\nQ: {q}")
        result = run_agent(q, thread_id)
        print(f"A: {result['answer']}")
        print(f"Messages in state: {result['message_count']}")
        print("-"*40)