from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.tools.comps_financial_calcs import calculate_blended_rent

def propose_comparables(state: DealState):
    """
    Step 3: Propose Comparables
    Finds and scores comps from memory/database.
    """
    print("--- Node: Propose Comparables ---")
    
    # Simulate finding comps
    response_content = (
        "I’ve identified 6 internal comparable logistics assets based on location, size, and specification.\n\n"
        "Recommended set (3):\n"
        "Comp A – 52k m², 4.5% yield, €82/m², 20 km away\n"
        "Comp B – 60k m², 4.7% yield, €85/m², 35 km away\n"
        "Comp C – 45k m², 4.4% yield, €87/m², 50 km away\n\n"
        "Current blended market rent from these 3 comps: €85/m²/year.\n\n"
        "Please remove any comps you don’t like or add others, and I’ll recompute the market rent."
    )
    
    # Mock data for state
    comps_data = [
        {"name": "Comp A", "size": "52k m2", "yield": "4.5%", "rent": "82", "dist": "20km"},
        {"name": "Comp B", "size": "60k m2", "yield": "4.7%", "rent": "85", "dist": "35km"},
        {"name": "Comp C", "size": "45k m2", "yield": "4.4%", "rent": "87", "dist": "50km"}
    ]
    
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
    
    # Mock database of available comps (including ones not currently selected)
    all_available_comps = [
        {"name": "Comp A", "size": "52k m2", "yield": "4.5%", "rent": "82", "dist": "20km"},
        {"name": "Comp B", "size": "60k m2", "yield": "4.7%", "rent": "85", "dist": "35km"},
        {"name": "Comp C", "size": "45k m2", "yield": "4.4%", "rent": "87", "dist": "50km"},
        {"name": "Comp D", "size": "75k m2", "yield": "4.8%", "rent": "80", "dist": "15km"}, # The XXL box
        {"name": "Comp E", "size": "40k m2", "yield": "4.3%", "rent": "90", "dist": "60km"},
    ]
    
    # Get current comps and last user message
    current_comps = state.get("comps_data", [])
    last_user_msg = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human" or getattr(msg, 'role', None) == "user":
            if isinstance(msg.content, list):
                last_user_msg = " ".join([
                    item.get("text", "") for item in msg.content 
                    if isinstance(item, dict) and item.get("type") == "text"
                ]).lower()
            else:
                last_user_msg = str(msg.content).lower()
            break
    
    # 1. Handle Removals
    updated_comps = []
    removed_names = []
    
    for comp in current_comps:
        comp_name = comp.get("name", "").lower()
        # Check if user wants to remove this comp
        if "remove" in last_user_msg and comp_name in last_user_msg:
            removed_names.append(comp.get("name"))
            continue  # Skip this comp (remove it)
        updated_comps.append(comp)

    # 2. Handle Additions
    added_names = []
    current_names = {c["name"] for c in updated_comps} # Names currently in the list (after removal)
    
    if "add" in last_user_msg:
        for candidate in all_available_comps:
            candidate_name = candidate.get("name", "")
            # Check if user wants to add this candidate AND it's not already in the list
            if candidate_name.lower() in last_user_msg and candidate_name not in current_names:
                updated_comps.append(candidate)
                added_names.append(candidate_name)
                current_names.add(candidate_name) # Prevent duplicates if logic runs multiple times

    # Generate response
    if removed_names or added_names:
        actions = []
        if removed_names:
            actions.append(f"Removing {', '.join(removed_names)}")
        if added_names:
            actions.append(f"Adding {', '.join(added_names)}")
            
        action_text = "; ".join(actions)
        
        # System log content
        status_content = (
            f"System Processing:\n"
            f"- {action_text}\n"
            f"- Recalculating blended market rent\n"
            f"- Updating deal state"
        )

        remaining_text = "\n".join([
            f"{c['name']} – {c['size']}, {c['yield']} yield, €{c['rent']}/m², {c['dist']} away"
            for c in updated_comps
        ])
        
        # Calculate new blended rent
        new_blended_rent = calculate_blended_rent(updated_comps)

        response_content = (
            f"I've updated the comparables set: {action_text}.\n\n"
            f"Updated comparables ({len(updated_comps)}):" + ("\n" + remaining_text if updated_comps else " None remaining.") + "\n\n"
            f"Updated blended market rent: €{new_blended_rent}/m²/year.\n\n"
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
        response_content = (
            "I couldn't identify which comparable to remove or add. "
            "Please specify the comp name (e.g., 'Remove Comp A' or 'Add Comp D')."
        )
    
    return {
        "messages": [AIMessage(content=response_content, name="agent")],
        "comps_data": updated_comps
    }

def comps_node(state: DealState):
    pass

