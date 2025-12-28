
import numpy_financial as npf

def calculate_metrics_test():
    # Inputs from user screenshot
    market_rent = 71.0
    area = 222221.0
    rent_growth = 0.03
    opex_ratio = 0.10
    entry_yield = 0.045
    exit_yield = 0.055
    ltv = 0.60
    interest_rate = 0.04
    capex = 0.0
    purchasers_costs = 0.0 # Assuming 0 based on screenshot not showing it

    # 1. Purchase Price
    initial_rent = market_rent * area # 15,777,691
    
    # Excel screenshot shows Initial Gross Income: 15,781,313.2
    # 15781313.2 / 222221 = 71.016299...
    # Let's use the exact value from Excel to match
    initial_rent = 15781313.2 
    
    net_purchase_price = initial_rent / entry_yield # 350,695,848.9
    purchase_price = net_purchase_price * (1 + purchasers_costs)
    loan_amount = purchase_price * ltv # 210,417,509.4
    equity_invested = purchase_price - loan_amount + capex # 140,278,339.6
    
    print(f"Purchase Price: {purchase_price:,.2f}")
    print(f"Loan Amount: {loan_amount:,.2f}")
    print(f"Equity Invested: {equity_invested:,.2f}")

    # 2. Cash Flows
    cash_flows = []
    current_rent = initial_rent
    
    for year in range(1, 11):
        if year > 1:
            current_rent *= (1 + rent_growth)
            
        noi = current_rent * (1 - opex_ratio)
        interest = loan_amount * interest_rate
        cash_flow = noi - interest
        cash_flows.append(cash_flow)
        print(f"Year {year} CF: {cash_flow:,.2f}")

    # 3. Exit
    exit_rent_forward = current_rent * (1 + rent_growth)
    exit_noi_forward = exit_rent_forward * (1 - opex_ratio)
    exit_value = exit_noi_forward / exit_yield
    net_sale_proceeds = exit_value - loan_amount
    
    print(f"Exit Value: {exit_value:,.2f}")
    print(f"Net Sale Proceeds: {net_sale_proceeds:,.2f}")
    
    cash_flows[-1] += net_sale_proceeds
    
    stream = [-equity_invested] + cash_flows
    irr = npf.irr(stream)
    
    # Equity Multiple Logic Check
    # Code says: (sum(cash_flows) + equity_invested) / equity_invested
    # Wait, sum(cash_flows) includes the net sale proceeds (which is profit + return of capital - debt repayment)
    # Net Sale Proceeds = Exit Value - Loan.
    # Equity Invested = Purchase Price - Loan.
    # So Net Sale Proceeds returns the equity portion of the exit value.
    # The stream is correct for IRR.
    # For EM: Total Cash Distributed / Equity Invested.
    # Total Cash Distributed = Sum of annual CFs (which includes Net Sale Proceeds).
    # The code adds `equity_invested` to `sum(cash_flows)`?
    # equity_multiple = (sum(cash_flows) + equity_invested) / equity_invested 
    # If cash_flows[-1] includes net_sale_proceeds, then sum(cash_flows) IS the total cash returned.
    # Why add equity_invested again? That seems wrong.
    
    em_wrong = (sum(cash_flows) + equity_invested) / equity_invested
    em_correct = sum(cash_flows) / equity_invested
    
    print(f"IRR: {irr:.4%}")
    print(f"EM (Current Code): {em_wrong:.2f}x")
    print(f"EM (Corrected): {em_correct:.2f}x")

calculate_metrics_test()
