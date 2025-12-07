from langchain_core.messages import AIMessage
from src.state import DealState

def propose_assumptions(state: DealState):
    """
    Step 6: Propose Assumptions
    Drafts assumptions based on tenancy and comps.
    """
    print("--- Node: Propose Assumptions ---")
    
    response_content = (
        "Based on the curated comparables and the tenancy schedule, here are my proposed underwriting assumptions:\n\n"
        "Rent & ERV\n"
        "Current passing rent: €78/m²/year (weighted from the rent roll)\n"
        "Blended market rent from comps: €83/m²/year\n"
        "Proposed ERV: €82/m²/year (slight discount to comps, given older spec and 11.6m eaves)\n\n"
        "Tenancy & Rollover (from tenancy schedule)\n"
        "Current occupancy: 100%\n"
        "WAULT to expiry: 4.3 years, with a large rollover in 2029 (60% of rent)\n"
        "Single-tenant risk: No\n"
        "Top 3 tenants represent 45% of total rent\n\n"
        "Reletting & Vacancy Assumptions\n"
        "Reletting downtime on expiries: 9 months (aligned with historical vacancy on comparable assets)\n"
        "Renewal probability: 65% for existing tenants, otherwise market ERV on relet\n\n"
        "Yields & Discount Rate\n"
        "Market evidence suggests yields between 4.5%–4.8% from comps\n"
        "Proposed exit yield: 4.75%\n"
        "Discount rate: 6.5%\n\n"
        "Please review and confirm or adjust any of these assumptions before I build the model."
    )
    
    # Mock data for state
    assumptions_data = {
        "growth": 0.03,
        "erv": 82,
        "exit_yield": 0.0475,
        "discount_rate": 0.065,
        "downtime": 9,
        "renewal_prob": 0.65
    }
    
    return {
        "messages": [AIMessage(content=response_content, name="agent")], 
        "financial_assumptions": assumptions_data
    }

def update_assumptions(state: DealState):
    """
    Step 8: Update Assumptions
    Writes final user assumptions to DealState.assumptions.
    """
    print("--- Node: Update Assumptions ---")
    # Placeholder logic
    return {"messages": [AIMessage(content="Updating financial assumptions...", name="system_log")]}

def assumptions_node(state: DealState):
    pass

