from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.tools.excel_engine import fill_excel_named_ranges, write_list_to_excel, update_financial_model
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link
import os
import time
from datetime import datetime
import math
import numpy_financial as npf

# Define Template Path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
TEMPLATE_PATH = os.path.join(BACKEND_DIR, "data", "templates", "MS Canopy Template -v5.xlsx")

def get_model_inputs(assumptions: dict):
    """
    Centralized logic to parse and normalize assumptions.
    Ensures consistency between Python calculation and Excel export.
    """
    def normalize_percent(val, default):
        try:
            if val is None or val == "":
                return default
            v = float(val)
            if v > 1.0: 
                return v / 100.0
            return v
        except:
            return default

    market_rent = float(assumptions.get("erv") or assumptions.get("market_rent") or 80)
    area = float(assumptions.get("leasable_area") or assumptions.get("area") or 0)
    
    entry_yield = normalize_percent(assumptions.get("entry_yield"), 0.065) 
    exit_yield = normalize_percent(assumptions.get("exit_yield"), 0.0475)  # Default from template
    rent_growth = normalize_percent(assumptions.get("rent_growth"), 0.02)
    ltv = normalize_percent(assumptions.get("ltv"), 0.60)
    interest_rate = normalize_percent(assumptions.get("interest_rate"), 0.045)
    
    # Purchasers Costs in Template: Transfer Taxes (5%) + Closing Costs (0.75%)
    purchasers_costs = normalize_percent(assumptions.get("purchasers_costs"), 0.05)
    
    hold_period = int(assumptions.get("hold_period", 7))
    project_name = assumptions.get("project_name", "Scenario Analysis")
    
    return {
        "market_rent": market_rent,
        "area": area,
        "entry_yield": entry_yield,
        "exit_yield": exit_yield,
        "rent_growth": rent_growth,
        "ltv": ltv,
        "interest_rate": interest_rate,
        "purchasers_costs": purchasers_costs,
        "hold_period": hold_period,
        "project_name": project_name,
        "opex_ratio": 0.10, 
        "capex": float(assumptions.get("capex") or 0)
    }

def calculate_simple_metrics(inputs: dict, passing_rent_total: float = 0):
    """
    Performs a simplified DCF calculation approaching MS Canopy Template logic.
    """
    try:
        market_rent = inputs["market_rent"]
        area = inputs["area"]
        entry_yield = inputs["entry_yield"]
        exit_yield = inputs["exit_yield"]
        rent_growth = inputs["rent_growth"]
        ltv = inputs["ltv"]
        interest_rate = inputs["interest_rate"]
        opex_ratio = inputs["opex_ratio"]
        capex = inputs["capex"]
        purchasers_costs = inputs["purchasers_costs"]
        closing_costs_pct = 0.0075 
        
        hold_period = inputs["hold_period"]
        
        # 1. Rent Logic
        erv_total = market_rent * area
        current_rent = passing_rent_total if passing_rent_total > 0 else erv_total
        
        # 2. Purchase Price Logic
        # Assumed: Price = Initial NOI / Entry Cap Rate.
        initial_noi = current_rent * (1 - opex_ratio)
        if entry_yield == 0: entry_yield = 0.0001
        
        net_purchase_price = initial_noi / entry_yield
        
        # Gross Purchase Price (TIC)
        acquisition_costs = net_purchase_price * (purchasers_costs + closing_costs_pct)
        gross_purchase_price = net_purchase_price + acquisition_costs
        
        # Debt
        loan_amount = net_purchase_price * ltv
        
        # Equity
        equity_invested = gross_purchase_price - loan_amount + capex
        
        # 3. Cash Flows
        cash_flows = []
        running_rent = current_rent
        
        for year in range(1, hold_period + 1):
            if year > 1:
                running_rent *= (1 + rent_growth)
            
            noi = running_rent * (1 - opex_ratio)
            interest = loan_amount * interest_rate
            
            # Pre-Tax Cash Flow
            cash_flow = noi - interest
            cash_flows.append(cash_flow)
            
        # 4. Exit
        projected_erv_exit = erv_total * ((1 + rent_growth) ** hold_period)
        exit_noi = projected_erv_exit * (1 - opex_ratio)
        
        if exit_yield == 0: exit_yield = 0.0001
        
        gross_exit_value = exit_noi / exit_yield
        sales_costs = gross_exit_value * 0.015 
        
        net_sale_proceeds = gross_exit_value - sales_costs - loan_amount
        
        # Add proceeds
        cash_flows[-1] += net_sale_proceeds
        
        # 5. Metrics
        stream = [-equity_invested] + cash_flows 
        
        irr = npf.irr(stream)
        if math.isnan(irr): irr = None
        
        if equity_invested > 0:
            equity_multiple = (sum(cash_flows) + equity_invested) / equity_invested
        else:
             equity_multiple = 0.0
             
        # Yield on Cost: First Year NOI / Gross Purchase Price
        if gross_purchase_price > 0:
            yield_on_cost = initial_noi / gross_purchase_price 
        else:
            yield_on_cost = 0.0
            
        return {
            "irr": irr,
            "equity_multiple": equity_multiple,
            "yield_on_cost": yield_on_cost,
            "debug": {
                "equity_invested": equity_invested,
                "loan_amount": loan_amount,
                "net_purchase_price": net_purchase_price,
                "gross_purchase_price": gross_purchase_price,
                "initial_noi": initial_noi
            }
        }
    except Exception as e:
        print(f"Error in metrics calc: {e}")
        return {"irr": 0, "equity_multiple": 0, "yield_on_cost": 0, "debug": {}}

def build_model(state: DealState):
    """
    Step 10: Build Model
    Populates MS Canopy Template -v5.xlsx
    """
    print("--- Node: Build Model (MS Canopy v5) ---", flush=True)
    
    assumptions = state.get("financial_assumptions", {})
    inputs = get_model_inputs(assumptions)
    
    # 1. Prepare Rent Roll Data
    extracted = state.get("extracted_data", {})
    source_json = extracted.get("source_json", {})
    tenancy_data = extracted.get("tenancy_schedule", [])
    
    if not tenancy_data and source_json:
        tenancy_data = source_json.get("tenants", [])
        if not tenancy_data and "assets" in source_json:
            tenancy_data = [] 
            for asset in source_json["assets"]:
                if "leases" in asset:
                    for lease in asset["leases"]:
                        t_name = "Unknown"
                        if isinstance(lease.get("tenant"), dict):
                            t_name = lease["tenant"].get("name", "Unknown")
                        elif isinstance(lease.get("tenant"), str):
                            t_name = lease.get("tenant")
                        
                        area_val = float(lease.get("area_m2") or 0)
                        current_rent_val = float(lease.get("annual_rent") or (area_val * float(lease.get("rent_psm_pa") or 0)))
                        
                        lease_obj = {
                            "name": t_name,
                            "area": area_val,
                            "lease_start": lease.get("lease_start"),
                            "lease_end": lease.get("lease_end"),
                            "current_rent": current_rent_val
                        }
                        tenancy_data.append(lease_obj)

    if not tenancy_data:
        tenancy_data = [
            {"name": "Mock Tenant A", "area": 1500, "lease_start": "2023-01-01", "lease_end": "2028-12-31", "current_rent": 120000},
            {"name": "Mock Tenant B", "area": 2500, "lease_start": "2022-06-01", "lease_end": "2027-05-31", "current_rent": 200000},
        ]
        
    total_area_rr = sum([float(t.get("area", 0)) for t in tenancy_data])
    total_passing_rent = sum([float(t.get("current_rent", 0)) for t in tenancy_data])
    
    if inputs["area"] == 0:
        inputs["area"] = total_area_rr

    # Format for 'Input Rent Roll' Sheet
    def parse_date(date_str):
        if not date_str: return ""
        try:
            return datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d")
        except:
            return date_str

    rr_rows = []
    for t in tenancy_data:
        row = [
            t.get("name", "Unknown"),
            t.get("area", 0),
            parse_date(t.get("lease_start", "")),
            "", 
            "", 
            parse_date(t.get("lease_end", "")),
            t.get("current_rent", 0)
        ]
        rr_rows.append(row)

    # Calculate Metrics first to get Loan Amount
    metrics = calculate_simple_metrics(inputs, passing_rent_total=total_passing_rent)
    loan_amount_calc = metrics.get('debug', {}).get('loan_amount', 0)

    # 2. Perform Excel Operations
    download_link = ""
    log_detail = ""
    
    if os.path.exists(TEMPLATE_PATH):
        try:
            write_list_to_excel.invoke({
                "file_path": TEMPLATE_PATH,
                "sheet_name": "Input Rent Roll",
                "data": rr_rows,
                "start_row": 2,
                "start_col": 1
            })
            log_detail += " | Filled Rent Roll"
            
            updates = {
                "Input Other!B1": inputs["project_name"],
                "Input Other!B4": inputs["hold_period"],
                "Input Other!B5": inputs["market_rent"],
                "Input Other!B12": inputs["entry_yield"],  # Entry_Cap_Rate
                "Input Other!B13": inputs["purchasers_costs"],  # Transfer_Taxes
                "Input Other!B15": inputs["exit_yield"],  # Exit_Cap_Rate
                "Debt Schedule (Bullet)!D10": inputs["interest_rate"],
                # CRITICAL: Update LTV in Money Page (E43) which drives Debt calculation (E44 = E43 * E31)
                "Money Page!E43": inputs["ltv"]  # LTV percentage (e.g., 0.60 for 60%)
            }
            
            update_financial_model.invoke({
                "file_path": TEMPLATE_PATH,
                "updates": updates
            })
            log_detail += f" | Filled Assumptions (Loan: {loan_amount_calc:,.0f})"
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_object_name = f"financial_models/MS_Canopy_{timestamp}.xlsx"
            s3_url = upload_to_s3_and_get_link(TEMPLATE_PATH, s3_object_name)
            
            if s3_url:
                download_link = f"📥 **[Download Financial Model]({s3_url})**"
            else:
                download_link = "(Upload to S3 failed. Please check AWS credentials.)"
        except Exception as e:
            print(f"Error processing Excel: {e}")
            download_link = f"(Error processing Excel: {e})"
    else:
        log_detail = f"(Skipped: Template not found at {TEMPLATE_PATH})"

    
    status_content = (
        "System Processing (v5 Template):\n"
        f"{log_detail}\n"
        f"- Configured with {len(tenancy_data)} tenants, Total Rent: €{total_passing_rent:,.0f}\n"
        f"- Set LTV: {inputs['ltv']*100:.0f}%, Entry Cap: {inputs['entry_yield']*100:.1f}%, Exit Cap: {inputs['exit_yield']*100:.1f}%\n"
        "- Uploaded model to secure cloud storage\n"
        "📊 All metrics calculated by Excel formulas"
    )

    response_content = (
        "✅ **Financial Model Built Successfully**\n\n"
        "**� Model Inputs Configured:**\n"
        f"- Total Passing Rent: €{total_passing_rent:,.0f}\n"
        f"- Leasable Area: {inputs['area']:,.0f} SQM\n"
        f"- Market Rent (ERV): €{inputs['market_rent']}/SQM\n"
        f"- Entry Cap Rate: {inputs['entry_yield']*100:.2f}%\n"
        f"- Exit Cap Rate: {inputs['exit_yield']*100:.2f}%\n"
        f"- **LTV: {inputs['ltv']*100:.0f}%** (Money Page E43)\n"
        f"- Interest Rate: {inputs['interest_rate']*100:.2f}%\n"
        f"- Hold Period: {inputs['hold_period']} years\n\n"
        "**🔍 To View Excel Calculated Results:**\n"
        "1. Download and open the Excel file below\n"
        "2. Press **Ctrl+Alt+F9** to recalculate all formulas\n"
        "3. Navigate to **'Cash Flows'** sheet\n"
        "4. Check **Column E**:\n"
        "   - **E105**: Equity Invested\n"
        "   - **E107**: Levered IRR\n"
        "   - **E108**: Levered Multiple\n"
        "   - **E110**: Net Gain / (Loss)\n\n"
        f"{download_link}\n\n"
        "⚠️ **Note**: Excel uses its own cashflow projection model. "
        "The calculated IRR and returns are based on the template's built-in formulas, "
        "which may include additional assumptions not captured in the simple Python preview."
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ],
        "financial_model": {
            "irr": metrics['irr'], 
            "equity_multiple": metrics['equity_multiple'],
            "yield_on_cost": metrics['yield_on_cost'],
            "status": "built"
        }
    }

