from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.nodes.model import get_model_inputs, calculate_simple_metrics

def prepare_scenario_analysis(state: DealState):
    """
    Step 13: Prepare Scenario Analysis
    Handles logic branch for scenario analysis.
    """
    print("--- Node: Prepare Scenario Analysis ---")
    return {"messages": [AIMessage(content="Ready for scenario analysis. Please specify a scenario (e.g., 'downside case with -5% rent').", name="agent")]}

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
    last_msg_lower = last_msg.lower()
    
    if "downside" in last_msg_lower:
        scenario_name = "Downside Case"
    elif "upside" in last_msg_lower:
        scenario_name = "Upside Case"
    elif "stress" in last_msg_lower:
        scenario_name = "Stress Test"
    
    status_content = (
        f"System Processing:\n"
        f"- Applying scenario: {scenario_name}\n"
        "- Adjusting market rent growth assumptions\n"
        "- Recalculating cash flows"
    )
    
    return {
        "messages": [AIMessage(content=status_content, name="system_log")],
        "current_scenario": scenario_name,
        "scenario_user_message": last_msg  # Save original message for parsing
    }

def rebuild_model_for_scenario(state: DealState):
    """
    Step 16: Rebuild Model for Scenario
    Re-runs the model with scenario assumptions.
    """
    print("--- Node: Rebuild Model for Scenario ---")
    
    scenario_name = state.get("current_scenario", "Scenario")
    user_message = state.get("scenario_user_message", "").lower()
    
    # Get base model metrics (saved before applying scenario)
    base_model = state.get("financial_model", {})
    base_irr = base_model.get("irr", 0)
    base_em = base_model.get("equity_multiple", 0)
    
    # Get current assumptions and apply scenario adjustments
    current_assumptions = state.get("financial_assumptions", {})
    scenario_assumptions = current_assumptions.copy()
    
    adjustments_applied = []
    
    # Parse user message for specific adjustments or apply defaults
    if "downside" in scenario_name.lower():
        # Downside: reduce market rent by 5%, increase exit yield by 25 bps
        scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * 0.95
        current_exit = scenario_assumptions.get("exit_yield", 0.0475)
        scenario_assumptions["exit_yield"] = current_exit + 0.0025  # +25 bps
        adjustments_applied.append("ERV -5%, Exit Yield +25bps")
    
    elif "upside" in scenario_name.lower():
        # Upside: increase market rent by 5%, decrease exit yield by 25 bps
        scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * 1.05
        current_exit = scenario_assumptions.get("exit_yield", 0.0475)
        scenario_assumptions["exit_yield"] = current_exit - 0.0025  # -25 bps
        adjustments_applied.append("ERV +5%, Exit Yield -25bps")
    
    elif "stress" in scenario_name.lower():
        # Stress: more aggressive downside
        scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * 0.90
        current_exit = scenario_assumptions.get("exit_yield", 0.0475)
        scenario_assumptions["exit_yield"] = current_exit + 0.0050  # +50 bps
        adjustments_applied.append("ERV -10%, Exit Yield +50bps")
    
    else:
        # For Custom Scenario, try to parse specific parameters from message
        # Default to a modest downside if no specific instructions
        scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * 0.97
        current_exit = scenario_assumptions.get("exit_yield", 0.0475)
        scenario_assumptions["exit_yield"] = current_exit + 0.0010  # +10 bps
        adjustments_applied.append("ERV -3%, Exit Yield +10bps (default adjustment)")
    
    print(f"[DEBUG] Applied adjustments: {adjustments_applied}")
    
    # Recalculate metrics with scenario assumptions
    try:
        inputs = get_model_inputs(scenario_assumptions)
        metrics = calculate_simple_metrics(inputs)
        scenario_irr = metrics.get("irr", 0) or 0
        scenario_em = metrics.get("equity_multiple", 0) or 0
        print(f"[DEBUG] Base IRR: {base_irr}, Base EM: {base_em}")
        print(f"[DEBUG] Scenario adjustments: {scenario_assumptions}")
        print(f"[DEBUG] Scenario IRR: {scenario_irr}, EM: {scenario_em}")
    except Exception as e:
        print(f"Error recalculating scenario metrics: {e}")
        scenario_irr = 0
        scenario_em = 0
    
    # Format percentages and multiples
    scenario_irr_pct = f"{scenario_irr*100:.1f}%"
    base_irr_pct = f"{base_irr*100:.1f}%"
    scenario_em_fmt = f"{scenario_em:.2f}x"
    base_em_fmt = f"{base_em:.2f}x"
    
    # Agent response with dynamic values
    response_content = (
        f"Model rebuilt for {scenario_name}.\n\n"
        "Scenario Impact:\n"
        f"- Levered IRR: {scenario_irr_pct} (vs {base_irr_pct} Base)\n"
        f"- Equity Multiple: {scenario_em_fmt} (vs {base_em_fmt} Base)"
    )
    
    return {"messages": [AIMessage(content=response_content, name="agent")]}

def wait_for_more_scenarios(state: DealState):
    """
    Step 18: Wait for More Scenarios
    Loop point.
    """
    print("--- Node: Wait for More Scenarios ---")
    return {"messages": [AIMessage(content="Waiting for more scenarios...", name="agent")]}

def scenarios_node(state: DealState):
    pass

