from langchain_core.messages import AIMessage
from src.state import DealState

def build_model(state: DealState):
    """
    Step 10: Build Model
    Calculates IRR, Multiple, YOC, etc., using current assumptions and leases.
    """
    print("--- Node: Build Model ---", flush=True)
    
    # Status update simulating system actions
    status_content = (
        "System Processing:\n"
        "- Fills named ranges in the Excel template\n"
        "- Runs the model and computes IRR, equity multiple, YoC, etc."
    )
    
    # Agent response
    response_content = (
        "Financial model built successfully.\n\n"
        "Key Returns:\n"
        "- Levered IRR: 18.5%\n"
        "- Equity Multiple: 2.1x\n"
        "- Yield on Cost: 6.8%\n\n"
        "Do you want to generate the presentation deck?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ],
        "financial_model": {"irr": 0.185, "em": 2.1, "status": "built"}
    }

def model_node(state: DealState):
    pass

