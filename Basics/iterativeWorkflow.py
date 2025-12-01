from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START,END
from typing import TypedDict,Annotated, Literal
from pydantic import Field, BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
import operator
load_dotenv()

generative_llm = ChatOpenAI(model='gpt-4o')
evaluate_llm =ChatOpenAI(model='gpt-4o-mini')
optimise_llm = ChatOpenAI(model='gpt-4o')

class EvluateSchema(BaseModel):
    evaluation: Literal["approved", "needs_improvement"] = Field(..., description="Final evaluation result.")
    feedback : str = Field(...,description="feedback for the tweet.")
    
structured_evaluate_llm = evaluate_llm.with_structured_output(EvluateSchema)

# State of Tweet
class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluate: Literal['approved', 'needs_improvement']
    feedback: str
    iteration: int
    max_itration: int
    
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]
    
def generate_tweet(state: TweetState)->TweetState:
    prompt = [
        SystemMessage(content="You are a Professional Twitter/X influenser"),
        HumanMessage(content=f"""
Write a short, original, and hilarious tweet on the topic: "{state['topic']}".

Rules:
- Do NOT use question-answer format.
- Max 280 characters.
- Use observational humor, irony, sarcasm, or cultural references.
- Think in meme logic, punchlines, or relatable takes.
- Use simple, day to day english
""")
    ]
    generated_tweet = generative_llm.invoke(prompt).content
    return {'tweet': generated_tweet, 'tweet_history': [generated_tweet]}


def evaluate_tweet(state: TweetState)-> TweetState:
    prompt =[
        SystemMessage(content="You are a ruthless, no-laugh-given Twitter critic. You evaluate tweets based on humor, originality, virality, and tweet format."),
        HumanMessage(content=f"""
Evaluate the following tweet:

Tweet: "{state['tweet']}"

Use the criteria below to evaluate the tweet:

1. Originality – Is this fresh, or have you seen it a hundred times before?  
2. Humor – Did it genuinely make you smile, laugh, or chuckle?  
3. Punchiness – Is it short, sharp, and scroll-stopping?  
4. Virality Potential – Would people retweet or share it?  
5. Format – Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke, and under 280 characters)?

Auto-reject if:
- It's written in question-answer format (e.g., "Why did..." or "What happens when...")
- It exceeds 280 characters
- It reads like a traditional setup-punchline joke
- Dont end with generic, throwaway, or deflating lines that weaken the humor (e.g., “Masterpieces of the auntie-uncle universe” or vague summaries)

### Respond ONLY in structured format:
- evaluation: "approved" or "needs_improvement"  
- feedback: One paragraph explaining the strengths and weaknesses 
"""),
        
    ]
    response = structured_evaluate_llm.invoke(prompt)
    return {'evaluate': response.evaluation, 'feedback': response.feedback, 'feedback_history':[response.feedback]}
    
def optimize_tweet(state: TweetState):
    prompt=[
        SystemMessage(content="You punch up tweets for virality and humor based on given feedback."),
        HumanMessage(content=f"""
Improve the tweet based on this feedback:
"{state['feedback']}"

Topic: "{state['topic']}"
Original Tweet:
{state['tweet']}

Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
""")
    ]
    
    response = optimise_llm.invoke(prompt).content
    itr= state['iteration']+1
    
    return {'tweet': response, 'iteration': itr}


def evaluation_decision(state: TweetState)-> Literal['approved', 'needs_improvement']:
    eval = state['evaluate']
    if eval == 'approved' or state['iteration'] >= state['max_itration']:
        return 'approved'
    else:
        return 'needs_improvement'
    
    
    
graph=StateGraph(TweetState)

graph.add_node("Generate Tweet", generate_tweet)
graph.add_node("Evaluate Tweet", evaluate_tweet)
graph.add_node("Optimize Tweet", optimize_tweet)


graph.add_edge(START, "Generate Tweet")
graph.add_edge("Generate Tweet", "Evaluate Tweet")
graph.add_conditional_edges("Evaluate Tweet",evaluation_decision,{'approved':END, 'needs_improvement': "Optimize Tweet"})
graph.add_edge("Optimize Tweet", "Evaluate Tweet")


workflow = graph.compile()

initial_state ={
    'topic': "AI ENGINEERS",
    'iteration':1,
    'max_itration': 5
}


final_state=workflow.invoke(initial_state)

print("Topic : ", final_state["topic"])
print("Tweet : ", final_state["tweet"])
print("Evalute : ", final_state["evaluate"])
print("Feedback : ", final_state["feedback"])
print("Iteration: ", final_state["iteration"])
print("Max Iteration : ", final_state["max_itration"])
print("Tweet History : ", final_state["tweet_history"])
print("Feed Back History : ", final_state["feedback_history"])

