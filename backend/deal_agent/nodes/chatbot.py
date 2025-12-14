from deal_agent.state import DealState
from deal_agent.utils.config import Config
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from deal_agent.tools.rag_tools import search_documents

# Initialize the LLM
# Ensure Config is imported so .env is loaded
llm = ChatOpenAI(model="gpt-5.2", temperature=0)

# Bind tools
tools = [search_documents]
llm_with_tools = llm.bind_tools(tools)

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
    response = llm_with_tools.invoke(messages)
    
    return {"messages": [response]}

def route_intent(state: DealState):
    """
    Router function to determine the next node based on state.
    """
    # Placeholder logic
    return "end"
