#  a kind of work flow in which multiple tool calls are made in a linear manner

# topic (input)-> outline (llm1) -> detail report (llm2) -> blog (output)


from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict
load_dotenv()


# 1. Define the State
class BlogState(TypedDict):
    topic:str
    outline: str
    report : str
    evaluate: str
    
# .... Defning Node functions
def outlineGenerator(state:BlogState)->BlogState:
    topic = state['topic']
    prompt=f"""Generate an outline for this Topic : {topic}"""
    llm = ChatOpenAI()
    response= llm.invoke(prompt).content
    state['outline']=response
    return state

def detailedReport(state: BlogState)-> BlogState:
    outline = state["outline"]
    prompt=f"You have to Generate  a detail Report according to this outline : {outline}"
    llm = ChatOpenAI()
    response = llm.invoke(prompt).content
    state['report'] = response
    return state
    
def evaluateReport(state:BlogState)->BlogState:
    topic=state['topic']
    report=state['report']
    prompt=f"You have to evaluate the Report based on the topic provided. For this Topic : {topic} i have written this report : {report}"
    llm = ChatOpenAI()
    response = llm.invoke(prompt).content
    state['evaluate']=response
    return state



# 2. Graph obj
graph = StateGraph(BlogState)

# 3. Nodes of graph
graph.add_node("OutlineGenerator", outlineGenerator)
graph.add_node("DetailedReport",detailedReport)
graph.add_node("Evaluate", evaluateReport)


# 4. Edges of Graph
graph.add_edge(START, "OutlineGenerator")
graph.add_edge("OutlineGenerator","DetailedReport")
graph.add_edge("DetailedReport", "Evaluate")
graph.add_edge("Evaluate", END)


# 5. compile the graph
workflow= graph.compile()

# 6. invoke it 
initial_state={'topic': 'Ai Engineers'}
final_state= workflow.invoke(initial_state)

print("Topic : ", final_state['topic'])
print("\nOutline : ",final_state['outline'])
print("\n\nDetailed Report : \n",final_state['report'])
print("\n\n Evaluation: ", final_state['evaluate'])