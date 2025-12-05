from langchain_core.messages import AIMessage
from src.state import DealState

def human_review_comps(state: DealState):
    """
    Step 4: Wait for Human (Comps)
    """
    print("--- Node: Human Review Comps ---")
    # The message is already sent by propose_comparables, so we can just return empty or a system prompt
    # But to be safe and clear, we can reiterate or just pass.
    # Let's keep it minimal as the previous node gave detailed instructions.
    return {} 

def human_review_assumptions(state: DealState):
    """
    Step 7: Wait for Human (Assumptions)
    """
    print("--- Node: Human Review Assumptions ---")
    # Message is sent by propose_assumptions
    return {}

def human_confirm_model_build(state: DealState):
    """
    Step 9: Wait for Human (Build Model)
    """
    print("--- Node: Human Confirm Model Build ---")
    return {"messages": [AIMessage(content="Assumptions updated. Ready to build the financial model?", name="agent")]}

def human_confirm_deck_generation(state: DealState):
    """
    Step 11: Wait for Human (Generate Deck)
    """
    print("--- Node: Human Confirm Deck Generation ---")
    return {"messages": [AIMessage(content="Financial model built. Do you want to generate the presentation deck?", name="agent")]}

def wait_for_scenario_requests(state: DealState):
    """
    Step 14: Wait for Scenario Requests
    """
    print("--- Node: Wait for Scenario Requests ---")
    return {"messages": [AIMessage(content="Ready for scenario analysis. Please specify a scenario (e.g., 'downside case with -5% rent').", name="agent")]}

