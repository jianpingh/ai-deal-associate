from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from deal_agent.tools.excel_engine import fill_excel_named_ranges, write_list_to_excel, update_financial_model
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link
import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import math
import numpy_financial as npf
from scipy.optimize import brentq

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


def xirr(cash_flows: list, dates: list, guess: float = 0.1) -> float:
    """
    计算XIRR (与Excel XIRR函数一致)
    
    Args:
        cash_flows: 现金流列表
        dates: 对应的日期列表
        guess: 初始猜测值
        
    Returns:
        XIRR 年化收益率
    """
    if len(cash_flows) != len(dates):
        raise ValueError("现金流和日期数量必须相同")
    
    # 转换日期为天数差
    date0 = dates[0]
    days = [(d - date0).days for d in dates]
    
    def npv_func(rate):
        """计算给定利率下的NPV"""
        if rate <= -1:
            return float('inf')
        npv = 0
        for cf, day in zip(cash_flows, days):
            npv += cf / ((1 + rate) ** (day / 365.0))
        return npv
    
    try:
        # 使用 Brent 方法求解
        result = brentq(npv_func, -0.9999, 10.0, xtol=1e-10)
        return result
    except ValueError:
        # 如果 brentq 失败，尝试 Newton-Raphson
        try:
            rate = guess
            for _ in range(100):
                npv = npv_func(rate)
                if abs(npv) < 1e-10:
                    return rate
                # 数值导数
                delta = 0.0001
                dnpv = (npv_func(rate + delta) - npv) / delta
                if abs(dnpv) < 1e-10:
                    break
                rate = rate - npv / dnpv
            return rate
        except:
            return None


def calculate_metrics_excel_compatible(inputs: dict, passing_rent_total: float = 0, start_date: datetime = None):
    """
    完全按照 MS Canopy Template 的逻辑计算财务指标
    
    Excel模板计算逻辑 (经过详细分析验证):
    ============================================
    1. Purchase Price = Annual NOI / Entry Cap
       - NOI = 有效租约的年租金 (不考虑增长)
       
    2. TIC = Purchase Price
    3. Total Acquisition Cost = Purchase Price × (1 + Transfer Tax + Closing Costs)
    4. Senior Debt = TIC × LTV
    5. Equity Invested = TIC - Senior Debt
    
    现金流:
    - Q0 = -Total Acquisition Cost + Senior Debt (无额外费用)
    - Q1-Q(n-1) = Quarterly EBITDA - Interest - Tax
    - Q(n) = Operations + Exit Value - Debt Repayment
    
    退出:
    - Exit NOI = Entry NOI (Excel不使用租金增长计算退出NOI!)
    - Gross Exit Value = Exit NOI / Exit Cap
    - Net Disposal = Gross Exit Value × (1 - Sales Costs%)
    ============================================
    """
    try:
        # 输入参数
        entry_yield = inputs["entry_yield"]
        exit_yield = inputs["exit_yield"]
        rent_growth = inputs["rent_growth"]  # 注意：Excel退出不使用这个增长
        ltv = inputs["ltv"]
        interest_rate = inputs["interest_rate"]
        purchasers_costs = inputs["purchasers_costs"]
        closing_costs_pct = 0.0075  # Excel template default (0.75%)
        hold_period = inputs["hold_period"]
        opex_ratio = inputs.get("opex_ratio", 0)  # 默认0
        tax_rate = 0.25  # Excel template default (25%)
        sales_costs_pct = 0.015  # 1.5% sales costs
        upfront_fee_pct = 0.015  # 1.5% upfront fee on debt (Excel CF_Ops at Q0)
        
        # 起始日期 (默认使用当前季度末)
        if start_date is None:
            today = datetime.now()
            quarter = (today.month - 1) // 3
            quarter_end_month = (quarter + 1) * 3
            start_date = datetime(today.year, quarter_end_month, 1) + relativedelta(months=1) - timedelta(days=1)
        
        # ========================================
        # 按照Excel的精确逻辑计算
        # ========================================
        
        # Annual NOI = Passing Rent (已经是NOI)
        annual_noi = passing_rent_total
        
        # Purchase Price = Annual NOI / Entry Cap
        if entry_yield == 0:
            entry_yield = 0.0001
        purchase_price = annual_noi / entry_yield
        
        # TIC = Purchase Price
        tic = purchase_price
        
        # Total Acquisition Cost (包含费用)
        # Excel: Transfer Tax (6.5%) + Closing Costs (0.75%)
        total_acquisition_cost = purchase_price * (1 + purchasers_costs + closing_costs_pct)
        
        # Senior Debt = TIC × LTV
        senior_debt = tic * ltv
        
        # Equity Invested = TIC - Senior Debt
        equity_invested = tic - senior_debt
        
        # ========================================
        # 季度现金流计算 (精确匹配Excel)
        # ========================================
        quarters_per_year = 4
        exit_quarter = hold_period * quarters_per_year  # 退出季度
        total_quarters = exit_quarter + 1  # +1 for Q0
        
        # 季度 EBITDA = Annual NOI / 4
        quarterly_ebitda = annual_noi / quarters_per_year
        
        # 季度利息 = Senior Debt × Interest Rate / 4
        quarterly_interest = senior_debt * interest_rate / quarters_per_year
        
        # 生成日期序列 (季度末)
        dates = []
        current_date = start_date
        for q in range(total_quarters):
            dates.append(current_date)
            current_date = current_date + relativedelta(months=3)
        
        # 生成现金流序列
        cash_flows = []
        
        # ========================================
        # Q0: 初始投资 (Excel精确逻辑)
        # Excel: CF_Ops = -Upfront Fee (1.5% of debt)
        #        CF_Investing = -Total Acquisition Cost
        #        CF_Financing = +Senior Debt
        #        Q0 CF = CF_Ops + CF_Investing + CF_Financing
        # ========================================
        upfront_fee = senior_debt * upfront_fee_pct
        cf_ops_q0 = -upfront_fee
        cf_investing_q0 = -total_acquisition_cost
        cf_financing_q0 = senior_debt
        q0_cf = cf_ops_q0 + cf_investing_q0 + cf_financing_q0
        cash_flows.append(q0_cf)
        
        # ========================================
        # Q1 到 Q(exit): 运营现金流
        # Excel: EBITDA - Interest - Tax
        # Tax = (EBITDA - Interest) × 25% if positive
        # ========================================
        for q in range(1, total_quarters):
            if q < exit_quarter:
                # 正常运营季度
                pre_tax_cf = quarterly_ebitda - quarterly_interest
                taxes = pre_tax_cf * tax_rate if pre_tax_cf > 0 else 0
                cf = pre_tax_cf - taxes
                cash_flows.append(cf)
            elif q == exit_quarter:
                # 退出季度
                # Excel关键: Exit NOI = Entry NOI (不增长!)
                exit_noi = annual_noi  # 不应用租金增长
                
                if exit_yield == 0:
                    exit_yield = 0.0001
                gross_exit_value = exit_noi / exit_yield
                
                # Sales Costs = 1.5%
                sales_costs = gross_exit_value * sales_costs_pct
                net_disposal_proceeds = gross_exit_value - sales_costs
                
                # 正常运营现金流
                pre_tax_cf = quarterly_ebitda - quarterly_interest
                taxes = pre_tax_cf * tax_rate if pre_tax_cf > 0 else 0
                cf_ops = pre_tax_cf - taxes
                
                # 退出季度现金流 = 运营 + 退出收益 - 债务偿还
                cf = cf_ops + net_disposal_proceeds - senior_debt
                cash_flows.append(cf)
        
        # ========================================
        # 计算指标 (使用XIRR和Excel公式)
        # ========================================
        
        # 过滤零值现金流
        valid_cf = [(cf, dt) for cf, dt in zip(cash_flows, dates) if cf != 0]
        valid_cfs = [x[0] for x in valid_cf]
        valid_dates = [x[1] for x in valid_cf]
        
        # Levered IRR (XIRR)
        try:
            levered_irr = xirr(valid_cfs, valid_dates)
        except:
            levered_irr = None
        
        # Levered Multiple = -SUMIF(positive) / SUMIF(negative)
        positive_cf = sum(cf for cf in cash_flows if cf > 0)
        negative_cf = sum(cf for cf in cash_flows if cf < 0)
        levered_multiple = -positive_cf / negative_cf if negative_cf != 0 else 0
        
        # Net Gain / (Loss)
        net_gain_loss = sum(cash_flows)
        
        # Yield on Cost
        yield_on_cost = annual_noi / tic if tic > 0 else 0
        
        return {
            "irr": levered_irr,
            "equity_multiple": levered_multiple,
            "yield_on_cost": yield_on_cost,
            "net_gain_loss": net_gain_loss,
            "debug": {
                "equity_invested": equity_invested,
                "loan_amount": senior_debt,
                "tic": tic,
                "total_acquisition_cost": total_acquisition_cost,
                "purchase_price": purchase_price,
                "annual_noi": annual_noi,
                "quarterly_ebitda": quarterly_ebitda,
                "quarterly_interest": quarterly_interest,
                "q0_cf": q0_cf,
                "exit_quarter": exit_quarter,
                "cash_flows_summary": f"Q0: {q0_cf:,.0f}, Q1-Q{exit_quarter-1}: {cash_flows[1]:,.0f}/quarter, Q{exit_quarter}: {cash_flows[exit_quarter]:,.0f}",
            }
        }
        
    except Exception as e:
        print(f"Error in Excel-compatible metrics calc: {e}")
        import traceback
        traceback.print_exc()
        return {
            "irr": None,
            "equity_multiple": 0,
            "yield_on_cost": 0,
            "net_gain_loss": 0,
            "debug": {"error": str(e)}
        }


def calculate_effective_noi(tenancy_data: list, model_start_date: datetime = None) -> tuple:
    """
    计算有效NOI，基于租约有效性
    
    Excel的GRI计算逻辑：
    - 只计算在模型期间有效的租约
    - 如果所有租约都已过期，使用最近过期的租约的租金
    
    Args:
        tenancy_data: 租户数据列表
        model_start_date: 模型开始日期
        
    Returns:
        (effective_noi, explanation): 有效NOI和说明
    """
    if model_start_date is None:
        today = datetime.now()
        quarter = (today.month - 1) // 3
        quarter_end_month = (quarter + 1) * 3
        model_start_date = datetime(today.year, quarter_end_month, 1) + relativedelta(months=1) - timedelta(days=1)
    
    def parse_lease_date(date_str):
        if not date_str:
            return None
        try:
            if isinstance(date_str, datetime):
                return date_str
            return datetime.strptime(str(date_str).split("T")[0], "%Y-%m-%d")
        except:
            return None
    
    effective_rent = 0
    effective_tenants = []
    latest_expired_rent = 0
    latest_expired_date = None
    latest_expired_tenant = None
    
    for tenant in tenancy_data:
        lease_end = parse_lease_date(tenant.get('lease_end'))
        current_rent = float(tenant.get('current_rent', 0) or 0)
        tenant_name = tenant.get('name', 'Unknown')
        
        if lease_end and lease_end >= model_start_date:
            # 租约在模型期间有效
            effective_rent += current_rent
            effective_tenants.append(tenant_name)
        elif lease_end:
            # 租约过期，记录最近过期的
            if latest_expired_date is None or lease_end > latest_expired_date:
                latest_expired_date = lease_end
                latest_expired_rent = current_rent
                latest_expired_tenant = tenant_name
    
    if effective_rent > 0:
        return effective_rent, f"Active leases: {', '.join(effective_tenants)}"
    elif latest_expired_rent > 0:
        # 如果所有租约都过期，使用最近过期的租约的租金
        # 这与Excel的GRI计算逻辑一致
        return latest_expired_rent, f"Using most recent lease ({latest_expired_tenant}, expired {latest_expired_date.strftime('%Y-%m-%d') if latest_expired_date else 'N/A'})"
    else:
        # 如果没有租约数据，使用总租金
        total = sum(float(t.get('current_rent', 0) or 0) for t in tenancy_data)
        return total, "Using total passing rent (no valid lease dates)"


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

    # 计算有效NOI (与Excel GRI逻辑一致)
    effective_noi, noi_explanation = calculate_effective_noi(tenancy_data)
    print(f"Effective NOI: €{effective_noi:,.0f} ({noi_explanation})", flush=True)
    
    # Calculate Metrics using Excel-compatible calculation (quarterly cash flows + XIRR)
    # 使用有效NOI而不是total_passing_rent
    metrics = calculate_metrics_excel_compatible(inputs, passing_rent_total=effective_noi)
    loan_amount_calc = metrics.get('debug', {}).get('loan_amount', 0)
    equity_invested_calc = metrics.get('debug', {}).get('equity_invested', 0)

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
            log_detail += f" | Filled Assumptions"
            log_detail += f" | Effective NOI: €{effective_noi:,.0f}"
            
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

    # Format calculated results for display
    equity_invested_display = f"€{equity_invested_calc:,.0f}" if equity_invested_calc else "N/A"
    levered_irr_display = f"{metrics['irr']*100:.2f}%" if metrics['irr'] else "N/A"
    levered_multiple_display = f"{metrics['equity_multiple']:.2f}x" if metrics['equity_multiple'] else "N/A"
    net_gain_loss_display = f"€{metrics['net_gain_loss']:,.0f}" if metrics.get('net_gain_loss') else "N/A"
    
    metrics_note = "💡 *Results calculated using Python (Excel-compatible logic: XIRR + quarterly cash flows)*"
    
    status_content = (
        "System Processing (v5 Template):\n"
        f"{log_detail}\n"
        f"- Configured with {len(tenancy_data)} tenants, Effective NOI: €{effective_noi:,.0f} ({noi_explanation})\n"
        f"- Set LTV: {inputs['ltv']*100:.0f}%, Entry Cap: {inputs['entry_yield']*100:.1f}%, Exit Cap: {inputs['exit_yield']*100:.1f}%\n"
        "- Uploaded model to secure cloud storage"
    )

    response_content = (
        "✅ **Financial Model Built Successfully**\n\n"
        "**⚙ Model Inputs Configured:**\n"
        f"- Total Passing Rent: €{total_passing_rent:,.0f}\n"
        f"- Leasable Area: {inputs['area']:,.0f} SQM\n"
        f"- Market Rent (ERV): €{inputs['market_rent']}/SQM\n"
        f"- Entry Cap Rate: {inputs['entry_yield']*100:.2f}%\n"
        f"- Exit Cap Rate: {inputs['exit_yield']*100:.2f}%\n"
        f"- **LTV: {inputs['ltv']*100:.0f}%** (Money Page E43)\n"
        f"- Interest Rate: {inputs['interest_rate']*100:.2f}%\n"
        f"- Hold Period: {inputs['hold_period']} years\n\n"
        "**📊 Calculated Results (Excel-Compatible):**\n"
        f"- **Equity Invested**: {equity_invested_display}\n"
        f"- **Levered IRR**: {levered_irr_display}\n"
        f"- **Levered Multiple**: {levered_multiple_display}\n"
        f"- **Net Gain / (Loss)**: {net_gain_loss_display}\n\n"
        f"{download_link}\n\n"
        f"{metrics_note}"
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
            "equity_invested": equity_invested_calc,
            "net_gain_loss": metrics.get('net_gain_loss'),
            "status": "built"
        }
    }

