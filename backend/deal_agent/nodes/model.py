from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.tools.excel_engine import fill_excel_named_ranges
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link
import os
import time
import numpy_financial as npf

def calculate_simple_metrics(assumptions: dict):
    """
    Performs a simplified 10-year DCF calculation to estimate returns.
    """
    # Extract assumptions with defaults
    market_rent = float(assumptions.get("market_rent", 85))
    area = 10000 # Mock area if not in state
    entry_yield = float(assumptions.get("entry_yield", 0.045))
    exit_yield = float(assumptions.get("exit_yield", 0.0475))
    rent_growth = float(assumptions.get("rent_growth", 0.03))
    ltv = float(assumptions.get("ltv", 0.60))
    interest_rate = float(assumptions.get("interest_rate", 0.04))
    
    # 1. Purchase Price
    initial_rent = market_rent * area
    purchase_price = initial_rent / entry_yield
    loan_amount = purchase_price * ltv
    equity_invested = purchase_price - loan_amount
    
    # 2. Cash Flows (10 Years)
    cash_flows = []
    current_rent = initial_rent
    
    for year in range(1, 11):
        # Simple growth
        current_rent *= (1 + rent_growth)
        noi = current_rent * 0.9 # 10% leakage/opex
        interest = loan_amount * interest_rate
        cash_flow = noi - interest
        cash_flows.append(cash_flow)
        
    # 3. Exit
    exit_noi = current_rent * 0.9
    exit_value = exit_noi / exit_yield
    net_sale_proceeds = exit_value - loan_amount # Repay debt
    
    # Add sale proceeds to last year's cash flow
    cash_flows[-1] += net_sale_proceeds
    
    # 4. Calculate Metrics
    # Stream: [-Equity, CF1, CF2, ..., CF10]
    stream = [-equity_invested] + cash_flows
    
    irr = npf.irr(stream)
    equity_multiple = (sum(cash_flows) + equity_invested) / equity_invested # Simplified EM
    yield_on_cost = (initial_rent * 0.9) / purchase_price # Initial YoC
    
    return {
        "irr": irr,
        "equity_multiple": equity_multiple,
        "yield_on_cost": yield_on_cost
    }

def build_model(state: DealState):
    """
    Step 10: Build Model
    Calculates IRR, Multiple, YOC, etc., using current assumptions and leases.
    """
    print("--- Node: Build Model ---", flush=True)
    
    # Prepare data for Excel
    # Mapping state keys to named ranges
    # We use safe defaults if keys are missing
    assumptions = state.get("assumptions", {})
    excel_inputs = {
        "Market_Rent": assumptions.get("market_rent", 0),
        "Exit_Yield": assumptions.get("exit_yield", 0),
        "CPI_Growth": assumptions.get("cpi", 0.02),
        # Add more mappings as needed
    }
    
    # --- Calculate Metrics Dynamically ---
    metrics = calculate_simple_metrics(assumptions)
    
    # Define template path
    # Use path relative to this file to ensure it works regardless of CWD
    # model.py is in backend/deal_agent/nodes/
    # Go up 2 levels: nodes -> deal_agent -> backend
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    template_path = os.path.join(backend_dir, "data", "templates", "financial_model_template.xlsx")
    
    print(f"DEBUG: Looking for template at: {template_path}")
    
    # Execute Excel update if template exists
    download_link = ""
    if os.path.exists(template_path):
        # fill_excel_named_ranges is a StructuredTool, so we must use .invoke()
        result = fill_excel_named_ranges.invoke({"file_path": template_path, "data": excel_inputs})
        log_detail = f"(Result: {result})"
        
        # Upload to S3
        try:
            timestamp = int(time.time())
            # Use deal_id if available, else 'temp'
            deal_id = state.get("deal_id", "temp")
            s3_object_name = f"financial_models/model_{deal_id}_{timestamp}.xlsx"
            
            s3_url = upload_to_s3_and_get_link(template_path, s3_object_name)
            
            if s3_url:
                download_link = f"📥 **[Download Financial Model (Excel)]({s3_url})**"
            else:
                download_link = "(Upload to S3 failed. Please check AWS credentials.)"
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            download_link = f"(Error uploading to S3: {e})"
    else:
        log_detail = "(Skipped: Template not found)"
    
    # Status update simulating system actions
    status_content = (
        "System Processing:\n"
        f"- Fills named ranges in the Excel template {log_detail}\n"
        "- Uploads model to secure cloud storage\n"
        "- Runs the model and computes IRR, equity multiple, YoC, etc."
    )
    
    # Format metrics for display
    irr_display = f"{metrics['irr']*100:.1f}%"
    em_display = f"{metrics['equity_multiple']:.2f}x"
    yoc_display = f"{metrics['yield_on_cost']*100:.1f}%"

    # Agent response
    response_content = (
        "Financial model built successfully.\n\n"
        "Key Returns (Estimated):\n"
        f"- Levered IRR: {irr_display}\n"
        f"- Equity Multiple: {em_display}\n"
        f"- Yield on Cost: {yoc_display}\n\n"
        f"{download_link}\n\n"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ],
        "financial_model": {
            "irr": metrics['irr'], 
            "em": metrics['equity_multiple'], 
            "status": "built"
        }
    }

def model_node(state: DealState):
    pass

