# lets make small chat bot using langgraph

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

load_dotenv()

llm = ChatOpenAI()

class ChatBotState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
def chatbot(state:ChatBotState)->ChatBotState:
    message= state['messages']
    response = llm.invoke(message)
    return {"messages": [response]}
    
graph = StateGraph(ChatBotState)
# checkpointer = InMemorySaver()
conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)

graph.add_node("Chat Bot", chatbot)
graph.add_edge(START, "Chat Bot")
graph.add_edge("Chat Bot", END)


chatbot= graph.compile(checkpointer=checkpointer)

intial_state = {
    "messages": "Write a 10 words essay on Ai"
}


def retrieve_all_threads():
    all_threads=set()
    for checkpoint in checkpointer.list(None):
        # print("\nCheck...........................",checkpoint)
        all_threads.add(checkpoint.config['configurable']['thread_id'])
        
    return list(all_threads)
