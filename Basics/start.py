# Components of Langgraph:
# 1. Nodes : (simple python functions that perform a task)
# 2. Edges : the linking between the Nodes
# 3. State: the mutable data that is shared and mutated by all the nodes of the StateGraph



from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict

load_dotenv()




# flow of application:
# Start -> height&weight -> node 1 (BMI calculator ) - > LLM (That will tell if the person's category) -> END

# 1. Define State
class BMIState(TypedDict):
    height : float
    weight: float
    result: float
    category : str
    advice: str
    
    
def bmi_calculator(state: BMIState)->BMIState:
    
    weight=state['weight']
    height = state['height']
    
    
    bmi = weight/(height**2)
    state['result']=bmi
    return state


def category_finder(state: BMIState)-> BMIState:
    bmi = state['result']

    if bmi < 18.5:
        state["category"] = "Underweight"
    elif 18.5 <= bmi < 25:
        state["category"] = "Normal"
    elif 25 <= bmi < 30:
        state["category"] = "Overweight"
    else:
        state["category"] = "Obese"
        
    return state

def advicer(state: BMIState)->BMIState:
    type = state['category']
    prompt = f"""Given the type of person what would you advice him or her for his health as an health Expert this is his type : {type}"""
    model = ChatOpenAI()
    response = model.invoke(prompt)
    state['advice']=response.content
    
    return state
    
    
# 2. Graph Object
graph = StateGraph(BMIState)

# 3. Nodes of the Graph
graph.add_node("Calculate_BMI", bmi_calculator)
graph.add_node("Category",category_finder)
graph.add_node("Advice", advicer)


# 4. Join the node by Edges
graph.add_edge(START, "Calculate_BMI")
graph.add_edge("Calculate_BMI", "Category")
graph.add_edge("Category", "Advice")
graph.add_edge("Advice", END)

# 5. Compile the Graph
workflow = graph.compile()


# invoke the graph
initial_state = {'height': 1.65, 'weight': 50}
final_state = workflow.invoke(initial_state)


print("\n Final State: ", final_state)






    
    
    
