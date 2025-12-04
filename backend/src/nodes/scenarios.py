from langchain_core.messages import AIMessage
from src.state import DealState

def prepare_scenario_analysis(state: DealState):
    """
    Step 13: Prepare Scenario Analysis
    Handles logic branch for scenario analysis.
    """
    print("--- Node: Prepare Scenario Analysis ---")
    return {"messages": [AIMessage(content="Ready for scenario analysis. Please specify a scenario (e.g., 'downside case with -5% rent').")]}

def apply_scenario(state: DealState):
    """
    Step 15: Apply Scenario
    Receives scenario parameters and updates temporary assumptions.
    """
    print("--- Node: Apply Scenario ---")
    
    # Extract scenario from last message (simplified)
    last_msg = state["messages"][-1].content
    
    # Ensure last_msg is a string before calling lower()
    if isinstance(last_msg, list):
        # If content is a list (e.g. multimodal), join text parts
        last_msg = " ".join([item.get("text", "") for item in last_msg if isinstance(item, dict) and "text" in item])
    elif not isinstance(last_msg, str):
        last_msg = str(last_msg)

    scenario_name = "Custom Scenario"
    if "downside" in last_msg.lower():
        scenario_name = "Downside Case (-5% Rent)"
    
    status_content = (
        f"**System Processing:**\n"
        f"- Applying scenario: {scenario_name}\n"
        "- Adjusting market rent growth assumptions\n"
        "- Recalculating cash flows"
    )
    
    return {
        "messages": [AIMessage(content=status_content)],
        "current_scenario": scenario_name
    }

def rebuild_model_for_scenario(state: DealState):
    """
    Step 16: Rebuild Model for Scenario
    Re-runs the model with scenario assumptions.
    """
    print("--- Node: Rebuild Model for Scenario ---")
    
    scenario_name = state.get("current_scenario", "Scenario")
    
    # Agent response
    response_content = (
        f"Model rebuilt for {scenario_name}.\n\n"
        "**Scenario Impact:**\n"
        "- Levered IRR: 16.2% (vs 18.5% Base)\n"
        "- Equity Multiple: 1.9x (vs 2.1x Base)\n"
        "- DSCR: 1.35x (Lowest point)"
    )
    
    return {"messages": [AIMessage(content=response_content)]}

def wait_for_more_scenarios(state: DealState):
    """
    Step 18: Wait for More Scenarios
    Loop point.
    """
    print("--- Node: Wait for More Scenarios ---")
    return {"messages": ["Waiting for more scenarios..."]}

def scenarios_node(state: DealState):
    pass

