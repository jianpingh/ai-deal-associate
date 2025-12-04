from langchain_core.messages import AIMessage
from src.state import DealState

def generate_deck(state: DealState):
    """
    Step 12: Generate Deck
    Produces a one-page summary or a full IC Deck.
    """
    print("--- Node: Generate Deck ---")
    
    # Status update simulating system actions
    status_content = (
        "System Processing:\n"
        "- Generates PPTX one-pager and IC deck\n"
        "- Sends link: Download IC Deck v1.pptx"
    )
    
    # Agent response
    response_content = (
        "IC deck generated (summary, market, tenancy, business plan, sensitivities, appendix).\n\n"
        "Would you like to run any scenarios (e.g. +5% ERV, +25 bps exit yield) and refresh key charts?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content),
            AIMessage(content=response_content)
        ],
        "deck_content": {"slides": ["Summary", "Market", "Tenancy", "Business Plan", "Sensitivities", "Appendix"]}
    }

def refresh_deck_views(state: DealState):
    """
    Step 17: Refresh Deck Views
    Updates or generates deck pages with scenario comparisons.
    """
    print("--- Node: Refresh Deck Views ---")
    
    # Status update
    status_content = (
        "System Processing:\n"
        "- Updates sensitivity tables in Deck\n"
        "- Refreshes return charts (IRR/EM vs Base Case)\n"
        "- Saves new version: Download IC Deck v2 (Scenario A).pptx"
    )
    
    # Agent response asking for more scenarios
    response_content = (
        "Deck views refreshed with the new scenario data.\n\n"
        "Would you like to run another scenario (e.g., 'stress test interest rates'), or is the analysis complete?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content),
            AIMessage(content=response_content)
        ]
    }

def deck_node(state: DealState):
    pass

