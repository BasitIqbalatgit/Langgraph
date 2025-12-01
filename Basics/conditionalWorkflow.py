from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START,END
from typing import Literal, TypedDict
from pydantic import BaseModel , Field

load_dotenv()

class SentimentSchema(BaseModel):
    sentiment: Literal['positive', 'negative'] = Field(description='Sentiment of the review')
class DiagnosisSchema(BaseModel):
    issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"] = Field(description='The category of issue mentioned in the review')
    tone: Literal["angry", "frustrated", "disappointed", "calm"] = Field(description='The emotional tone expressed by the user')
    urgency: Literal["low", "medium", "high"] = Field(description='How urgent or critical the issue appears to be')    

model = ChatOpenAI(model='gpt-4o-mini')
sentiment_structured_output_model = model.with_structured_output(SentimentSchema)
diagnosis_structured_output_model = model.with_structured_output(DiagnosisSchema)


class SentimentState(TypedDict):
    review: str
    sentiment: Literal['positive', 'negative']
    diagnosis: dict
    respose: str


def find_sentiment(state: SentimentState)-> SentimentState:
    prompt = f'For the following review find out the sentiment \n {state['review']}'
    sentiment = sentiment_structured_output_model.invoke(prompt).sentiment
    return {'sentiment': sentiment} 

def check_condition(state: SentimentState)-> Literal['positive_response','run_diagnosis']:
    if state['sentiment'] == 'positive':
        return 'positive_response'
    else:
        return 'run_diagnosis'

def run_diagnosis(state: SentimentState)->SentimentState:
    prompt = f"""Diagnose this negative review:\n\n{state['review']}\n"
    "Return issue_type, tone, and urgency."""
    
    respone = diagnosis_structured_output_model.invoke(prompt)
    return {'diagnosis':respone.model_dump()} # model dump is used to convert this pydantic obj to dict

def positive_response(state: SentimentState)-> SentimentState:
    prompt = f"""Write a warm thank-you message in response to this review:
    \n\n\"{state['review']}\"\n
Also, kindly ask the user to leave feedback on our website."""
    response = model.invoke(prompt).content
    return {'respose': response}
    
def negative_response(state: SentimentState)-> SentimentState:
    diagnosis = state['diagnosis']
    prompt = f"""You are a support assistant.
The user had a '{diagnosis['issue_type']}' issue, sounded '{diagnosis['tone']}', and marked urgency as '{diagnosis['urgency']}'.
Write an empathetic, helpful resolution message.
"""
    response = model.invoke(prompt).content
    return {'respose': response}
   
graph = StateGraph(SentimentState)

graph.add_node("find_sentiment", find_sentiment)
graph.add_node("run_diagnosis", run_diagnosis)
graph.add_node("positive_response",positive_response)
graph.add_node("negative_response",negative_response)

graph.add_edge(START,"find_sentiment")
graph.add_conditional_edges("find_sentiment",check_condition)
graph.add_edge('run_diagnosis', 'negative_response')
graph.add_edge('negative_response', END)
graph.add_edge('positive_response', END)


wrokflow = graph.compile()

intial_state={
    'review': "I’ve been trying to log in for over an hour now, and the app keeps freezing on the authentication screen. I even tried reinstalling it, but no luck. This kind of bug is unacceptable, especially when it affects basic functionality."
}

final_state= wrokflow.invoke(intial_state)

# print("Final State : ",final_state.keys())
print("Review: ", final_state['review'])
print("Sentiment : ", final_state['sentiment'])
print("Response : ", final_state['respose'])