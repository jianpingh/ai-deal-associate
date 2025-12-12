from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from deal_agent.state import DealState
from deal_agent.tools.assumptions_tools import process_assumption_updates, fetch_default_assumptions
from deal_agent.tools.comps_tools import calculate_blended_rent
import json

def propose_assumptions(state: DealState):
    """
    Step 6: Propose Assumptions
    Drafts assumptions based on tenancy and comps.
    """
    print("--- Node: Propose Assumptions ---")
    
    # 1. Gather Context Data
    extracted = state.get("extracted_data", {})
    analysis_text = extracted.get("analysis", "")
    source_json = extracted.get("source_json", {})
    
    # Get Comps Data
    comps_data = state.get("comps_data", [])
    blended_rent = calculate_blended_rent(comps_data) if comps_data else 85.0 # Fallback
    
    # Get Default Assumptions (Base)
    assumptions_data = fetch_default_assumptions()
    
    # 2. Use LLM to generate the detailed proposal
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""
    You are a Real Estate Investment Analyst.
    
    **Context:**
    - **Comps Blended Rent**: €{blended_rent}/m²/year
    - **Ingestion Analysis**: {analysis_text[:2000]}
    - **Structured Data**: {json.dumps(source_json, indent=2)[:1000]}
    - **Default Market Assumptions**: {json.dumps(assumptions_data, indent=2)}
    
    **Task:**
    Generate a detailed "Underwriting Assumptions" proposal. 
    You MUST explicitly reference the tenancy schedule (from ingestion analysis) and the comps.
    
    **Required Output Format:**
    
    > Based on the curated comparables and the tenancy schedule, here are my proposed underwriting assumptions:
    > 
    > **Rent & ERV**
    > • Current passing rent: [Extract from data or estimate] (weighted from the rent roll)
    > • Blended market rent from comps: €{blended_rent}/m²/year
    > • Proposed ERV: **[Value]** (Provide rationale, e.g., discount/premium to comps)
    > 
    > **Tenancy & Rollover** (from tenancy schedule)
    > • Current occupancy: **[Value]%**
    > • WAULT to expiry: **[Value] years**, [Mention any major rollover risks if found in analysis]
    > • Single-tenant risk: **[Yes/No]**
    > • Top 3 tenants represent **[Value]%** of total rent (Estimate if not exact)
    > 
    > **Reletting & Vacancy Assumptions**
    > • Reletting downtime on expiries: **{assumptions_data.get('downtime', 9)} months** (aligned with historical vacancy)
    > • Renewal probability: **{int(assumptions_data.get('renewal_prob', 0.65)*100)}%** for existing tenants
    > 
    > **Yields & Discount Rate**
    > • Market evidence suggests yields between [Range]% from comps
    > • Proposed exit yield: **{assumptions_data.get('exit_yield', 0.0475)*100}%**
    > • Discount rate: **{assumptions_data.get('discount_rate', 0.065)*100}%**
    > 
    > Please **review and confirm or adjust** any of these assumptions before I build the model.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        "messages": [AIMessage(content=response.content, name="agent")], 
        "financial_assumptions": assumptions_data
    }

def update_assumptions(state: DealState):
    """
    Step 8: Update Assumptions
    Writes final user assumptions to DealState.assumptions.
    """
    print("--- Node: Update Assumptions ---")
    
    # Get current assumptions and last user message
    current_assumptions = state.get("financial_assumptions", {})
    last_user_msg = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human" or getattr(msg, 'role', None) == "user":
            if isinstance(msg.content, list):
                last_user_msg = " ".join([
                    item.get("text", "") for item in msg.content 
                    if isinstance(item, dict) and item.get("type") == "text"
                ])
            else:
                last_user_msg = str(msg.content)
            break
            
    # Use tool to process updates
    updated_assumptions = process_assumption_updates(current_assumptions, last_user_msg)
    
    # Generate log message
    changes = []
    for k, v in updated_assumptions.items():
        if v != current_assumptions.get(k):
            changes.append(f"{k}: {v}")
            
    if changes:
        log_msg = f"Updated assumptions: {', '.join(changes)}"
    else:
        log_msg = "No specific assumption updates detected."

    return {
        "messages": [AIMessage(content=log_msg, name="system_log")],
        "financial_assumptions": updated_assumptions
    }

def assumptions_node(state: DealState):
    pass
