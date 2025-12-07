from langchain_core.messages import AIMessage
from src.state import DealState

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
    
    # Parse the removal request (simple keyword matching)
    updated_comps = []
    removed_names = []
    
    for comp in current_comps:
        comp_name = comp.get("name", "").lower()
        # Check if user wants to remove this comp
        if "remove" in last_user_msg and comp_name in last_user_msg:
            removed_names.append(comp.get("name"))
            continue  # Skip this comp (remove it)
        updated_comps.append(comp)
    
    # Generate response
    if removed_names:
        removed_text = ", ".join(removed_names)
        
        # System log content
        status_content = (
            f"System Processing:\n"
            f"- Removing comparables: {removed_text}\n"
            f"- Recalculating blended market rent\n"
            f"- Updating deal state"
        )

        remaining_text = "\n".join([
            f"{c['name']} – {c['size']}, {c['yield']} yield, €{c['rent']}/m², {c['dist']} away"
            for c in updated_comps
        ])
        
        response_content = (
            f"I've removed {removed_text} from the comparables set.\n\n"
            f"Updated comparables ({len(updated_comps)}):" + ("\n" + remaining_text if updated_comps else " None remaining.") + "\n\n"
            "Recalculating blended market rent based on remaining comps...\n\n"
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
            "I couldn't identify which comparable to remove. "
            "Please specify the comp name (e.g., 'Remove Comp A')."
        )
    
    return {
        "messages": [AIMessage(content=response_content, name="agent")],
        "comps_data": updated_comps
    }

def comps_node(state: DealState):
    pass

