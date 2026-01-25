# Financial Model Calculation Guide

## Overview

This document describes the calculation methodology for the real estate financial model, covering both the Excel template (MS Canopy Template -v5.xlsx) and the Python implementation (`model.py`). Both implementations produce identical results.

---

## Key Output Metrics

| Metric | Description | Excel Location |
|--------|-------------|----------------|
| **Equity Invested** | Initial equity required from investor | Money Page E45 |
| **Levered IRR** | Internal Rate of Return using XIRR | Cash Flows (calculated) |
| **Levered Multiple** | Total returns / Initial investment | Cash Flows (calculated) |
| **Net Gain / (Loss)** | Total profit or loss from investment | Cash Flows (sum) |

---

## Input Parameters

| Parameter | Default Value | Description | Excel Location |
|-----------|---------------|-------------|----------------|
| Entry Cap Rate | 6.50% | Capitalization rate for purchase | Input Other B12 |
| Exit Cap Rate | 4.75% | Capitalization rate for sale | Input Other B15 |
| LTV | 60% | Loan-to-Value ratio | Money Page E43 |
| Interest Rate | 4.50% | Annual interest rate on debt | Debt Schedule D10 |
| Transfer Taxes | 5.00% | Purchase transaction taxes | Input Other B13 |
| Closing Costs | 0.75% | Purchase closing costs | Template default |
| Hold Period | 7 years | Investment holding period | Input Other B4 |
| Tax Rate | 25% | Income tax rate | Template default |
| Sales Costs | 1.50% | Disposal transaction costs | Template default |
| Upfront Fee | 1.50% | Debt origination fee | Template default |

---

## Calculation Flow

### Step 1: Gross Rental Income (GRI) / Effective NOI

**Critical Concept**: The model uses "Effective NOI" rather than total passing rent.

#### Excel Logic (GRI Sheet):
- Only counts rent from leases **valid during the model period**
- If all leases have expired, uses the **most recently expired** lease's rent
- This ensures the model reflects realistic income expectations

#### Python Implementation:
```python
def calculate_effective_noi(tenancy_data, model_start_date):
    effective_rent = 0
    for tenant in tenancy_data:
        lease_end = parse_date(tenant['lease_end'])
        if lease_end >= model_start_date:
            # Lease is valid - include in effective NOI
            effective_rent += tenant['current_rent']
    
    if effective_rent == 0:
        # All leases expired - use most recent expired lease
        effective_rent = latest_expired_lease['current_rent']
    
    return effective_rent
```

#### Example:
| Tenant | Annual Rent | Lease End | Status |
|--------|-------------|-----------|--------|
| Tenant A | €1,000,000 | 2024-12-31 | ❌ Expired |
| Tenant B | €409,491 | 2029-03-31 | ✅ Valid |
| Tenant C | €222,215 | 2023-06-30 | ❌ Expired |

**Result**: Effective NOI = €409,491 (only Tenant B is valid)

---

### Step 2: Purchase Price Calculation

**Formula**:
```
Purchase Price = Annual NOI / Entry Cap Rate
```

#### Excel:
- Location: Money Page E31
- Formula: `= GRI_Total / Entry_Cap_Rate`

#### Python:
```python
annual_noi = effective_noi  # From Step 1
purchase_price = annual_noi / entry_yield  # e.g., 409,491 / 0.065 = 6,299,862
```

---

### Step 3: Total Investment Cost (TIC)

**Formula**:
```
TIC = Purchase Price × (1 + Transfer Taxes + Closing Costs)
```

#### Excel:
- Location: Money Page E32
- Formula: `= E31 * (1 + Transfer_Taxes + Closing_Costs)`

#### Python:
```python
total_acquisition_cost = purchase_price * (1 + purchasers_costs + closing_costs_pct)
# e.g., 6,299,862 * (1 + 0.05 + 0.0075) = 6,662,104
```

---

### Step 4: Debt Calculation

**Formula**:
```
Senior Debt = TIC × LTV
```

#### Excel:
- Location: Money Page E44
- Formula: `= E43 * E31` (LTV × Purchase Price)

#### Python:
```python
senior_debt = tic * ltv  # e.g., 6,299,862 * 0.60 = 3,779,917
```

---

### Step 5: Equity Invested

**Formula**:
```
Equity Invested = TIC - Senior Debt
```

#### Excel:
- Location: Money Page E45
- Formula: `= E32 - E44`

#### Python:
```python
equity_invested = tic - senior_debt  # e.g., 6,299,862 - 3,779,917 = 2,519,945
```

---

### Step 6: Quarterly Cash Flows

The model uses **quarterly cash flows** for accurate XIRR calculation.

#### Q0 (Initial Investment Quarter):

**Formula**:
```
Q0 = -Total Acquisition Cost + Senior Debt - Upfront Fee
```

| Component | Calculation | Example |
|-----------|-------------|---------|
| CF_Investing | -Total Acquisition Cost | -€6,662,104 |
| CF_Financing | +Senior Debt | +€3,779,917 |
| CF_Ops | -Upfront Fee (1.5% of debt) | -€56,699 |
| **Q0 Total** | Sum | **-€2,938,886** |

#### Python:
```python
upfront_fee = senior_debt * 0.015
q0_cf = -total_acquisition_cost + senior_debt - upfront_fee
```

---

#### Q1 to Q(n-1) (Operating Quarters):

**Formula**:
```
Quarterly CF = EBITDA - Interest - Tax
```

| Component | Calculation | Example |
|-----------|-------------|---------|
| Quarterly EBITDA | Annual NOI / 4 | €409,491 / 4 = €102,373 |
| Quarterly Interest | Debt × Rate / 4 | €3,779,917 × 4.5% / 4 = €42,524 |
| Pre-Tax CF | EBITDA - Interest | €59,849 |
| Tax (25%) | Pre-Tax × 25% | €14,962 |
| **Net CF** | Pre-Tax - Tax | **€44,887** |

#### Python:
```python
quarterly_ebitda = annual_noi / 4
quarterly_interest = senior_debt * interest_rate / 4
pre_tax_cf = quarterly_ebitda - quarterly_interest
taxes = pre_tax_cf * 0.25 if pre_tax_cf > 0 else 0
cf = pre_tax_cf - taxes
```

---

#### Q(n) (Exit Quarter):

**Key Point**: Excel does **NOT** apply rent growth to Exit NOI!

**Formula**:
```
Exit NOI = Entry NOI (no growth)
Gross Exit Value = Exit NOI / Exit Cap Rate
Net Disposal = Gross Exit Value × (1 - Sales Costs)
Q(n) = Operating CF + Net Disposal - Debt Repayment
```

| Component | Calculation | Example |
|-----------|-------------|---------|
| Exit NOI | Same as Entry NOI | €409,491 |
| Gross Exit Value | NOI / Exit Cap | €409,491 / 4.75% = €8,621,073 |
| Sales Costs (1.5%) | Gross × 1.5% | €129,316 |
| Net Disposal | Gross - Costs | €8,491,757 |
| Operating CF | Same as other quarters | €44,887 |
| Debt Repayment | -Senior Debt | -€3,779,917 |
| **Q(n) Total** | Sum | **€4,756,727** |

#### Python:
```python
# Critical: No rent growth for exit
exit_noi = annual_noi  # NOT annual_noi * (1 + rent_growth) ** hold_period

gross_exit_value = exit_noi / exit_yield
net_disposal = gross_exit_value * (1 - 0.015)
cf_exit = cf_ops + net_disposal - senior_debt
```

---

### Step 7: Metrics Calculation

#### Levered IRR (using XIRR)

**Excel Function**: `=XIRR(cash_flows, dates)`

**Python Implementation**:
```python
def xirr(cash_flows, dates, guess=0.1):
    """
    Calculate XIRR using Brent's method
    """
    date0 = dates[0]
    days = [(d - date0).days for d in dates]
    
    def npv_func(rate):
        npv = 0
        for cf, day in zip(cash_flows, days):
            npv += cf / ((1 + rate) ** (day / 365.0))
        return npv
    
    # Solve for rate where NPV = 0
    result = brentq(npv_func, -0.9999, 10.0)
    return result
```

---

#### Levered Multiple

**Formula**:
```
Multiple = -SUM(positive cash flows) / SUM(negative cash flows)
```

#### Python:
```python
positive_cf = sum(cf for cf in cash_flows if cf > 0)
negative_cf = sum(cf for cf in cash_flows if cf < 0)
levered_multiple = -positive_cf / negative_cf
```

---

#### Net Gain / (Loss)

**Formula**:
```
Net Gain = SUM(all cash flows)
```

---

## Cash Flow Timeline Example (7-Year Hold)

| Quarter | Date | Cash Flow | Description |
|---------|------|-----------|-------------|
| Q0 | 2025-03-31 | -€2,938,886 | Initial investment |
| Q1 | 2025-06-30 | €44,887 | Operating |
| Q2 | 2025-09-30 | €44,887 | Operating |
| ... | ... | ... | ... |
| Q27 | 2031-12-31 | €44,887 | Operating |
| Q28 | 2032-03-31 | €4,756,727 | Exit + Operations |

**Total Cash Flows**: 29 periods (Q0 to Q28)

---

## Verification Results

With the following inputs:
- Effective NOI: €409,491
- Entry Cap: 6.50%
- Exit Cap: 4.75%
- LTV: 60%
- Interest Rate: 4.50%
- Hold Period: 7 years

| Metric | Python | Excel | Match |
|--------|--------|-------|-------|
| Equity Invested | €2,519,945 | €2,519,945 | ✅ |
| Levered IRR | 12.30% | 12.30% | ✅ |
| Levered Multiple | 2.03x | 2.03x | ✅ |

---

## Key Differences: Python vs Simple DCF

| Aspect | Simple DCF | Excel-Compatible (Current) |
|--------|------------|---------------------------|
| Cash Flow Frequency | Annual | **Quarterly** |
| IRR Method | NPF.IRR | **XIRR with dates** |
| Exit NOI | With rent growth | **No rent growth** |
| NOI Source | Total passing rent | **Effective NOI** |
| Tax | Often ignored | **25% on positive income** |
| Upfront Fee | Not included | **1.5% of debt** |

---

## File References

- **Python Model**: [backend/deal_agent/nodes/model.py](backend/deal_agent/nodes/model.py)
- **Excel Engine**: [backend/deal_agent/tools/excel_engine.py](backend/deal_agent/tools/excel_engine.py)
- **Excel Template**: `backend/data/templates/MS Canopy Template -v5.xlsx`

---

## Appendix: Excel Sheet Structure

| Sheet Name | Purpose |
|------------|---------|
| Input Rent Roll | Tenant data input |
| Input Other | Assumptions (cap rates, hold period, etc.) |
| GRI | Gross Rental Income calculation |
| Money Page | TIC, Debt, Equity calculations |
| Debt Schedule (Bullet) | Debt terms and interest |
| Cash Flows | Quarterly cash flow model |
| Exit | Exit value calculations |
