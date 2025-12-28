from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.nodes.model import get_model_inputs, calculate_simple_metrics
from deal_agent.tools.excel_engine import fill_excel_named_ranges, write_list_to_excel
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link
import os
import time
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def parse_scenario_parameters(message: str):
    """
    Uses LLM to extract scenario parameters from natural language.
    """
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a financial modeling assistant. Extract scenario assumptions from the user's message. "
             "Look for changes in 'Market Rent' (ERV) and 'Exit Yield' (Cap Rate). "
             "Return a JSON object with exactly these keys:\n"
             "- 'erv_change_pct': float (e.g., -0.05 for -5%, 0.05 for +5%). Default to 0 if not found.\n"
             "- 'exit_yield_change_bps': float (e.g., 25 for +25bps, -10 for -10bps). Default to 0 if not found.\n"
             "Do not include markdown formatting like ```json.\n"
             "IMPORTANT: If the user provides a list of changes (e.g. 'ERV +5%, Exit Yield -25 bps'), extract ALL of them."
            ),
            ("user", "{message}")
        ])
        chain = prompt | llm | JsonOutputParser()
        return chain.invoke({"message": message})
    except Exception as e:
        print(f"[WARNING] LLM parsing failed: {e}")
        return {"erv_change_pct": 0, "exit_yield_change_bps": 0}

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
    
    # Extract scenario from last HUMAN message
    last_msg = ""
    for msg in reversed(state["messages"]):
        if msg.type == "human" or getattr(msg, "role", "") == "user":
            last_msg = msg.content
            break
            
    print(f"[DEBUG] apply_scenario captured message: '{last_msg}'")
    
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
    user_message = state.get("scenario_user_message", "")
    
    # Fallback: If empty, try to find the last user message again
    if not user_message:
        for msg in reversed(state["messages"]):
            if msg.type == "human" or getattr(msg, "role", "") == "user":
                user_message = str(msg.content)
                break
    
    user_message = user_message.lower()
    
    # Get base model metrics (saved before applying scenario)
    base_model = state.get("financial_model", {})
    base_irr = base_model.get("irr", 0)
    base_em = base_model.get("equity_multiple", 0)
    base_yoc = base_model.get("yield_on_cost", 0)
    
    # Get current assumptions and apply scenario adjustments
    current_assumptions = state.get("financial_assumptions", {})
    scenario_assumptions = current_assumptions.copy()
    
    # Sync keys for consistency (Ensure 'erv' and 'market_rent' are aligned)
    if "market_rent" in scenario_assumptions and "erv" not in scenario_assumptions:
        scenario_assumptions["erv"] = scenario_assumptions["market_rent"]
    if "erv" in scenario_assumptions and "market_rent" not in scenario_assumptions:
        scenario_assumptions["market_rent"] = scenario_assumptions["erv"]
    
    adjustments_applied = []
    
    # 1. Try to parse specific parameters using LLM (Semantic Parsing)
    print(f"[DEBUG] Parsing scenario message: '{user_message}'")
    parsed_params = parse_scenario_parameters(user_message)
    print(f"[DEBUG] LLM Parsed params: {parsed_params}")
    
    erv_change = parsed_params.get("erv_change_pct", 0)
    yield_change_bps = parsed_params.get("exit_yield_change_bps", 0)
    
    # Fallback: If LLM returned 0s, try simple regex for common patterns
    if erv_change == 0 and yield_change_bps == 0:
        import re
        # Regex for ERV/Rent (Improved to handle spaces)
        # Matches: "erv + 5 %", "rent -5%", "erv 5%"
        erv_match = re.search(r"(?:erv|rent).*?([+-]?\s*\d+(?:\.\d+)?)\s*%", user_message)
        if erv_match:
            # Remove spaces from the number string (e.g. "+ 5" -> "+5")
            val_str = erv_match.group(1).replace(" ", "")
            erv_change = float(val_str) / 100.0
            print(f"[DEBUG] Regex found ERV change: {erv_change}")
            
        # Regex for Exit Yield (Improved to handle spaces)
        # Matches: "exit yield + 25 bps", "cap rate -0.25 %"
        yield_match = re.search(r"(?:exit|yield|cap).*?([+-]?\s*\d+(?:\.\d+)?)\s*(bps|%)", user_message)
        if yield_match:
            val_str = yield_match.group(1).replace(" ", "")
            val = float(val_str)
            unit = yield_match.group(2)
            if unit == "bps":
                yield_change_bps = val
            else:
                yield_change_bps = val * 100
            print(f"[DEBUG] Regex found Yield change bps: {yield_change_bps}")
    
    # Force custom params if regex found something, even if LLM failed
    has_custom_params = (erv_change != 0 or yield_change_bps != 0)
    
    if has_custom_params:
        # Apply parsed custom values (Overrides named scenario defaults)
        if erv_change != 0:
            scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * (1 + erv_change)
            adjustments_applied.append(f"ERV {erv_change*100:+.1f}%")
            
        if yield_change_bps != 0:
            current_exit = scenario_assumptions.get("exit_yield", 0.0475)
            scenario_assumptions["exit_yield"] = current_exit + (yield_change_bps / 10000.0)
            adjustments_applied.append(f"Exit Yield {yield_change_bps:+.0f}bps")
            
    # 2. If no specific parameters found, fall back to named scenario defaults
    elif "downside" in scenario_name.lower():
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
        # Default fallback for Custom Scenario if no numbers were parsed
        scenario_assumptions["erv"] = scenario_assumptions.get("erv", 85) * 0.97
        current_exit = scenario_assumptions.get("exit_yield", 0.0475)
        scenario_assumptions["exit_yield"] = current_exit + 0.0010  # +10 bps
        adjustments_applied.append("ERV -3%, Exit Yield +10bps (default adjustment)")
    
    print(f"[DEBUG] Applied adjustments: {adjustments_applied}")
    
    # Sync back market_rent for deck generation
    if "erv" in scenario_assumptions:
        scenario_assumptions["market_rent"] = scenario_assumptions["erv"]
    
    # Recalculate metrics with scenario assumptions
    metrics = {}
    try:
        inputs = get_model_inputs(scenario_assumptions)
        metrics = calculate_simple_metrics(inputs)
        scenario_irr = metrics.get("irr", 0) or 0
        scenario_em = metrics.get("equity_multiple", 0) or 0
        scenario_yoc = metrics.get("yield_on_cost", 0) or 0
        print(f"[DEBUG] Base IRR: {base_irr}, Base EM: {base_em}")
        print(f"[DEBUG] Scenario adjustments: {scenario_assumptions}")
        print(f"[DEBUG] Scenario IRR: {scenario_irr}, EM: {scenario_em}")
    except Exception as e:
        print(f"Error recalculating scenario metrics: {e}")
        scenario_irr = 0
        scenario_em = 0
        scenario_yoc = 0
        metrics = {"irr": 0, "equity_multiple": 0, "yield_on_cost": 0}

    # --- Product Logic: Calculate Deltas & Generate Insights ---

    # 1. Calculate Deltas (Changes)
    irr_delta_bps = (scenario_irr - base_irr) * 10000 # Basis points
    em_delta = scenario_em - base_em
    
    # 2. Generate Automated Insight (Simple Rule-based)
    insight = ""
    # Thresholds (can be configurable)
    HURDLE_RATE = 0.10 
    SIGNIFICANT_DROP_BPS = -300 # -3% IRR drop is significant

    if scenario_irr < HURDLE_RATE:
        insight = "⚠️ **Risk Alert**: Returns fall below typical hurdle rates (10%) in this scenario. The deal may be too risky."
    elif irr_delta_bps < SIGNIFICANT_DROP_BPS:
        insight = "ℹ️ **Sensitivity**: The project is highly sensitive to these assumptions. Returns drop significantly."
    elif abs(irr_delta_bps) < 50:
        insight = "✅ **Resilient**: The project returns are very stable. This scenario has minimal impact."
    else:
        insight = "📉 **Impact**: Moderate impact on returns, but the project remains viable."

    # --- Generate Excel Model for Scenario ---
    download_link = ""
    try:
        # Prepare inputs for Excel
        excel_inputs = {
            "Market_Rent": inputs["market_rent"],
            "Area": inputs["area"],
            "Exit_Yield": inputs["exit_yield"],
            "Rent_Growth": inputs["rent_growth"],
            "Entry_Yield": inputs["entry_yield"],
            "LTV": inputs["ltv"],
            "Interest_Rate": inputs["interest_rate"],
            "OpEx_Ratio": inputs["opex_ratio"],
            "Capex": inputs["capex"]
        }
        
        # Locate template
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        template_path = os.path.join(backend_dir, "data", "templates", "financial_model_template.xlsx")
        
        if os.path.exists(template_path):
            # Update Excel with scenario assumptions
            fill_excel_named_ranges.invoke({"file_path": template_path, "data": excel_inputs})
            
            # Upload to S3
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            deal_id = state.get("deal_id", "temp")
            # Sanitize scenario name for filename
            safe_scenario_name = "".join([c if c.isalnum() else "_" for c in scenario_name])
            s3_object_name = f"financial_models/Financial_Model_{safe_scenario_name}_{timestamp}.xlsx"
            
            s3_url = upload_to_s3_and_get_link(template_path, s3_object_name)
            
            if s3_url:
                download_link = f"📥 **[Download Financial_Model]({s3_url})**"
    except Exception as e:
        print(f"Error generating scenario Excel: {e}")

    # 3. Format Response (Professional Structure)
    scenario_irr_pct = f"{scenario_irr*100:.1f}%"
    base_irr_pct = f"{base_irr*100:.1f}%"
    scenario_em_fmt = f"{scenario_em:.2f}x"
    base_em_fmt = f"{base_em:.2f}x"
    scenario_yoc_pct = f"{scenario_yoc*100:.2f}%"
    base_yoc_pct = f"{base_yoc*100:.2f}%"
    
    # Format adjustments list
    adjustments_str = "\n".join([f"- {adj}" for adj in adjustments_applied])

    # Handle generic scenario name in header
    header_suffix = f": {scenario_name}" if scenario_name != "Scenario" else ""

    response_content = (
        f"### 📊 Scenario Analysis{header_suffix}\n\n"
        f"**Assumptions Applied:**\n"
        f"{adjustments_str}\n\n"
        f"**Key Outcomes:**\n"
        f"- 10-year leveraged IRR: {scenario_irr_pct} (vs Base {base_irr_pct}, {irr_delta_bps:+.0f} bps)\n"
        f"- Equity multiple: {scenario_em_fmt} (vs Base {base_em_fmt}, {em_delta:+.2f}x)\n"
        f"- Yield on cost at stabilisation: {scenario_yoc_pct} (vs Base {base_yoc_pct})\n\n"
        f"The financial model has been rebuilt.\n\n"
        f"{download_link}\n\n"
        f"{insight}"
    )
    
    return {
        "messages": [AIMessage(content=response_content, name="agent")],
        "financial_model": metrics,
        "financial_assumptions": scenario_assumptions
    }

def wait_for_more_scenarios(state: DealState):
    """
    Step 18: Wait for More Scenarios
    Loop point.
    """
    print("--- Node: Wait for More Scenarios ---")
    return {"messages": [AIMessage(content="Waiting for more scenarios...", name="agent")]}

def scenarios_node(state: DealState):
    pass

