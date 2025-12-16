from deal_agent.state import DealState
from deal_agent.utils.config import Config
from langchain_core.messages import AIMessage, ToolMessage, SystemMessage
from langchain_openai import ChatOpenAI
from deal_agent.tools.rag_tools import search_documents

# Initialize the LLM
# Ensure Config is imported so .env is loaded
llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

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
    
    # Sanitize messages to handle dangling tool calls (OpenAI 400 Error)
    # If an AIMessage has tool_calls but is not followed by a ToolMessage, the API will fail.
    sanitized_messages = []
    for i, msg in enumerate(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            # Check if the next message is a ToolMessage
            has_tool_response = False
            if i + 1 < len(messages):
                next_msg = messages[i+1]
                if isinstance(next_msg, ToolMessage):
                    has_tool_response = True
            
            if not has_tool_response:
                # Found a dangling tool call. Strip it to prevent API error.
                content = msg.content if msg.content else "(Interrupted tool call)"
                sanitized_messages.append(AIMessage(content=content))
            else:
                sanitized_messages.append(msg)
        else:
            sanitized_messages.append(msg)

    # Inject Context
    context_str = ""
    if state.get("current_deal_id"):
        context_str += f"Current Deal ID: {state['current_deal_id']}\n"
    if state.get("company_name"):
        context_str += f"Company: {state['company_name']}\n"
    
    system_msg = SystemMessage(content=f"""You are an AI Deal Associate.
{context_str}
You have access to tools to search documents. Use them when asked about specific deal details.
If you don't know the Deal ID, ask the user or assume 'default_deal' if testing.
""")
    
    final_messages = [system_msg] + sanitized_messages

    # Call LLM with sanitized history
    response = llm_with_tools.invoke(final_messages)
    
    return {"messages": [response]}

def route_intent(state: DealState):
    """
    Router function to determine the next node based on state.
    """
    # Placeholder logic
    return "end"
