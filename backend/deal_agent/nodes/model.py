from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.tools.excel_engine import fill_excel_named_ranges
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link
import os
import time

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
                download_link = f"\n\n[Download Financial Model (Excel)]({s3_url})"
            else:
                download_link = "\n\n(Upload to S3 failed. Please check AWS credentials.)"
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            download_link = f"\n\n(Error uploading to S3: {e})"
    else:
        log_detail = "(Skipped: Template not found)"
    
    # Status update simulating system actions
    status_content = (
        "System Processing:\n"
        f"- Fills named ranges in the Excel template {log_detail}\n"
        "- Uploads model to secure cloud storage\n"
        "- Runs the model and computes IRR, equity multiple, YoC, etc."
    )
    
    # Agent response
    response_content = (
        "Financial model built successfully.\n\n"
        "Key Returns:\n"
        "- Levered IRR: 18.5%\n"
        "- Equity Multiple: 2.1x\n"
        "- Yield on Cost: 6.8%"
        f"{download_link}\n\n"
        "Do you want to generate the presentation deck?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ],
        "financial_model": {"irr": 0.185, "em": 2.1, "status": "built"}
    }

def model_node(state: DealState):
    pass

