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
    
    # Extract Area from Source JSON if available
    assets = source_json.get("assets", [])
    if assets:
        # Try to get area from the first asset's logistics_asset field
        logistics_asset = assets[0].get("logistics_asset", {})
        area_m2 = logistics_asset.get("area_m2")
        if area_m2:
            assumptions_data["area"] = float(area_m2)
            assumptions_data["leasable_area"] = float(area_m2)

    # Update default assumptions with blended rent from comps
    assumptions_data["market_rent"] = blended_rent
    assumptions_data["erv"] = blended_rent
    
    # 2. Use LLM to generate the detailed proposal
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    prompt = f"""
    You are a Real Estate Investment Analyst.
    
    **Context:**
    - **Comps Blended Rent**: €{blended_rent}/m²/year
    - **Ingestion Analysis**: {analysis_text[:2000]}
    - **Structured Data**: {json.dumps(source_json, indent=2)[:1000]}
    - **Default Market Assumptions**: {json.dumps(assumptions_data, indent=2)}
    
    **CRITICAL INSTRUCTION ON CURRENCY:**
    - The target model MUST be in **EUROS (€)**.
    - The source data might be in GBP (£) or other currencies.
    - **YOU MUST CONVERT ALL FIGURES TO EUROS (€) PSM (Per Square Meter).**
    - Use conversion rate: **1 GBP = 1.2 EUR**.
    - Use unit conversion: **1 sq ft = 0.0929 sq m** (or Price PSF * 10.764 = Price PSM).
    - If the source rent is ~£4-6, it is likely GBP PSF. Convert it: £5.5 PSF * 10.764 * 1.2 ≈ €71 PSM.
    - **DO NOT output GBP (£) figures in the final proposal.** All figures must be € PSM.

    **Task:**
    Generate a detailed "Underwriting Assumptions" proposal. 
    You MUST explicitly reference the tenancy schedule (from ingestion analysis) and the comps.
    
    **Required Output Format:**
    
    Based on the curated comparables and the tenancy schedule, here are my proposed underwriting assumptions:
    
    **Rent & ERV**
    
    • Current passing rent: **£[Value] PSF** / **€[Value] PSM**
      *(Calculation: Source Rent £[Value] PSF * 10.764 * 1.2 ≈ €[Value] PSM)*
    
    • Blended market rent from comps: €{blended_rent}/m²/year
    
    • Proposed ERV: **€[Value]/m²/year**
      *(Rationale: [Provide rationale, e.g., discount/premium to comps])*
    
    **Tenancy & Rollover** (from tenancy schedule)
    
    • Current occupancy: **[Value]%**
    
    • WAULT to expiry: **[Value] years**, [Mention any major rollover risks if found in analysis]
    
    • Single-tenant risk: **[Yes/No]**
    
    • Top 3 tenants represent **[Value]%** of total rent (Estimate if not exact)
    
    **Reletting & Vacancy Assumptions**
    
    • Reletting downtime on expiries: **{assumptions_data.get('downtime', 9)} months** (aligned with historical vacancy)
    
    • Renewal probability: **{int(assumptions_data.get('renewal_prob', 0.65)*100)}%** for existing tenants
    
    **Yields & Discount Rate**
    
    • Market evidence suggests yields between [Range]% from comps
    
    • Proposed exit yield: **{assumptions_data.get('exit_yield', 0.0475)*100}%**
    
    • Discount rate: **{assumptions_data.get('discount_rate', 0.065)*100}%**
    
    Please **review and confirm or adjust** any of these assumptions before I build the model.
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
            # Format values for display
            display_val = v
            if k in ['exit_yield', 'entry_yield', 'discount_rate', 'growth', 'interest_rate', 'ltv', 'renewal_prob']:
                display_val = f"{v*100:.1f}%"
            elif k == 'downtime':
                display_val = f"{v} months"
            
            # Format key for display
            display_key = k.replace('_', ' ')
            
            changes.append(f"{display_key} = {display_val}")
            
    if changes:
        # Store the changes string in state so the next node can use it
        formatted_changes = "; ".join(changes)
        return {
            "financial_assumptions": updated_assumptions,
            "last_assumption_changes": formatted_changes # Pass to next node
        }
    else:
        return {
            "financial_assumptions": updated_assumptions,
            "last_assumption_changes": "No changes detected"
        }

def assumptions_node(state: DealState):
    pass
