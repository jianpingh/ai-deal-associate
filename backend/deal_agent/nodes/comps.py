from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from deal_agent.state import DealState
from deal_agent.tools.comps_tools import calculate_blended_rent, fetch_market_comparables
import json

def propose_comparables(state: DealState):
    """
    Step 3: Propose Comparables
    Finds and scores comps from memory/database.
    """
    print("--- Node: Propose Comparables ---")
    
    # Try to get location from extracted data
    location = None
    extracted = state.get("extracted_data", {})
    assets = extracted.get("assets", [])
    if assets:
        # Use the city of the first asset as the primary location context
        location = assets[0].get("city")
        if not location:
            location = assets[0].get("country")
            
    # Fetch comps from Pinecone
    # If location is found (e.g. "Daventry"), it will search "Logistics market comparables in Daventry"
    all_comps = fetch_market_comparables(location=location)
    
    # Simple logic: take top 5 as proposal (Pinecone returns top_k=10)
    comps_data = all_comps[:5]
    
    # Calculate blended rent for the proposed set
    blended_rent = calculate_blended_rent(comps_data)
    
    # Format the list for display
    comps_list_text = "\n\n".join([
        f"• {c['name']} – {c['size']}, {c['yield']} yield, €{c['rent']}/m², {c['dist']} away"
        for c in comps_data
    ])
    
    response_content = (
        f"I’ve identified {len(all_comps)} internal comparable logistics assets based on location ({location or 'General'}) and specification.\n\n"
        f"Recommended set ({len(comps_data)}):\n\n"
        f"{comps_list_text}\n\n"
        f"Current blended market rent from these {len(comps_data)} comps: **€{blended_rent}/m²/year**.\n\n"
        "Please **remove any comps you don’t like or add others**, and I’ll recompute the market rent."
    )
    
    return {
        "messages": [AIMessage(content=response_content, name="agent")], 
        "comps_data": comps_data
    }

def update_comparables(state: DealState):
    """
    Step 5: Update Comparables
    Recalculates blended market metrics based on user-curated comps.
    """
    print("--- Node: Update Comparables ---")
    
    # Try to get location from extracted data
    location = None
    extracted = state.get("extracted_data", {})
    assets = extracted.get("assets", [])
    if assets:
        location = assets[0].get("city") or assets[0].get("country")

    # Fetch all available comps from tool to handle additions
    all_available_comps = fetch_market_comparables(location=location)
    current_comps = state.get("comps_data", [])
    
    # Get last user message
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
            
    # --- Use LLM to understand intent ---
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    available_names = [c["name"] for c in all_available_comps]
    current_names = [c["name"] for c in current_comps]
    
    prompt = f"""
    You are managing a list of Real Estate Comparables.
    
    Current List: {current_names}
    Available Database: {available_names}
    
    User Request: "{last_user_msg}"
    
    Analyze the user's request and determine which comps to ADD or REMOVE.
    Synonyms for REMOVE: delete, drop, exclude, get rid of, minus.
    Synonyms for ADD: include, plus, insert.
    
    Return a JSON object with two lists: "to_add" and "to_remove".
    Example: {{"to_add": ["Comp D"], "to_remove": ["Comp A"]}}
    If no specific comp is mentioned or the request is unclear, return empty lists.
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        # Clean up response content to ensure it's valid JSON
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        actions = json.loads(content)
        to_add = actions.get("to_add", [])
        to_remove = actions.get("to_remove", [])
        
    except Exception as e:
        print(f"LLM parsing failed: {e}")
        to_add = []
        to_remove = []

    # --- Execute Actions ---
    updated_comps = list(current_comps) # Copy
    
    # 1. Handle Removals
    if to_remove:
        updated_comps = [c for c in updated_comps if c["name"] not in to_remove]

    # 2. Handle Additions
    if to_add:
        current_names_set = {c["name"] for c in updated_comps}
        for name in to_add:
            if name not in current_names_set:
                # Find the comp object in all_available_comps
                candidate = next((c for c in all_available_comps if c["name"] == name), None)
                if candidate:
                    updated_comps.append(candidate)
                    current_names_set.add(name)

    # Generate response
    if to_remove or to_add:
        action_desc = []
        if to_remove:
            action_desc.append(f"Removed {', '.join(to_remove)}")
        if to_add:
            action_desc.append(f"Added {', '.join(to_add)}")
            
        status_content = (
            "- Updates comparable set\n"
            "- Recomputes market rent benchmark (and optionally yield benchmark)"
        )
        
        # Recalculate metrics
        new_blended_rent = calculate_blended_rent(updated_comps)
        
        # Get just the names for the summary
        comp_names = [c['name'].replace("Comp ", "") for c in updated_comps]
        comp_names_str = ",".join(comp_names)
        
        response_content = (
            f"Done\n\n"
            f"Final comparable set ({len(updated_comps)}): {comp_names_str}\n\n"
            f"Updated Blended Market Rent: **€{new_blended_rent}/m²/year**.\n\n"
            "Would you like to proceed to financial assumptions?"
        )
        
        return {
            "messages": [
                AIMessage(content=status_content, name="system_log"),
                AIMessage(content=response_content, name="agent")
            ],
            "comps_data": updated_comps
        }
    else:
        return {
            "messages": [
                AIMessage(content="I couldn't identify which comparable to remove or add. Please specify the comp name (e.g., 'Remove Comp A' or 'Add Comp D').", name="agent")
            ]
        }

def comps_node(state: DealState):
    pass

