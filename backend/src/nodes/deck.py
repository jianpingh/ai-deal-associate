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
        "**System Processing:**\n"
        "- Generates PPTX one-pager and IC deck\n"
        "- Sends link: [Download IC Deck v1.pptx]"
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
    # Placeholder logic
    return {"messages": ["Deck views refreshed."]}

def deck_node(state: DealState):
    pass

