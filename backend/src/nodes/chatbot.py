from src.state import DealState
from src.utils.config import Config
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

# Initialize the LLM
# Ensure Config is imported so .env is loaded
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def chatbot_node(state: DealState):
    """
    Node for general chatbot interaction and intent recognition.
    Corresponds to processes:
    18. Q&A / Due Diligence Support
    """
    print("--- Node: Chatbot ---")
    
    # Get messages from state
    messages = state["messages"]
    
    # Call LLM
    response = llm.invoke(messages)
    
    return {"messages": [response]}

def route_intent(state: DealState):
    """
    Router function to determine the next node based on state.
    """
    # Placeholder logic
    return "end"
