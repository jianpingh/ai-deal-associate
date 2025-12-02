from src.state import DealState

def human_review_comps(state: DealState):
    """
    Step 4: Wait for Human (Comps)
    """
    print("--- Node: Human Review Comps ---")
    return {"messages": ["Comparables proposed. Please review and curate them in the UI, then confirm to proceed."]}

def human_review_assumptions(state: DealState):
    """
    Step 7: Wait for Human (Assumptions)
    """
    print("--- Node: Human Review Assumptions ---")
    return {"messages": ["Assumptions proposed. Please review LTV, exit cap, etc., and apply changes."]}

def human_confirm_model_build(state: DealState):
    """
    Step 9: Wait for Human (Build Model)
    """
    print("--- Node: Human Confirm Model Build ---")
    return {"messages": ["Assumptions updated. Ready to build the financial model?"]}

def human_confirm_deck_generation(state: DealState):
    """
    Step 11: Wait for Human (Generate Deck)
    """
    print("--- Node: Human Confirm Deck Generation ---")
    return {"messages": ["Financial model built. Do you want to generate the presentation deck?"]}

def wait_for_scenario_requests(state: DealState):
    """
    Step 14: Wait for Scenario Requests
    """
    print("--- Node: Wait for Scenario Requests ---")
    return {"messages": ["Ready for scenario analysis. Please specify a scenario (e.g., 'downside case with -5% rent')."]}
