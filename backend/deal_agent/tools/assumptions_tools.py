import re

def process_assumption_updates(current_assumptions: dict, user_input: str) -> dict:
    """
    Parses user input to update financial assumptions.
    Supports updates for: growth, exit yield, discount rate, ERV, downtime, renewal probability.
    """
    updated = current_assumptions.copy()
    # Normalize input: replace underscores with spaces to handle "entry_yield" style inputs
    user_input_lower = user_input.lower().replace("_", " ")

    # Helper to extract percentage (returns float 0.05 for 5%)
    def extract_percent(text):
        match = re.search(r"(\d+(\.\d+)?)%", text)
        if match:
            return float(match.group(1)) / 100
        return None

    # Helper to extract number (returns float)
    def extract_number(text):
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            return float(match.group(1))
        return None

    # 1. Growth
    if "growth" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["growth"] = val

    # 2. Exit Yield
    if "exit yield" in user_input_lower or "cap rate" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["exit_yield"] = val

    # 3. Discount Rate
    if "discount" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["discount_rate"] = val

    # 4. ERV (Rent)
    if "erv" in user_input_lower or "market rent" in user_input_lower:
        # Look for number near the keyword, potentially ignoring "€"
        # Simple extraction for now
        val = extract_number(user_input_lower.split("erv")[-1] if "erv" in user_input_lower else user_input_lower)
        if val is not None:
            updated["erv"] = val

    # 5. Downtime
    if "downtime" in user_input_lower or "void" in user_input_lower:
        val = extract_number(user_input_lower)
        if val is not None:
            updated["downtime"] = int(val)

    # 6. Renewal Probability
    if "renewal" in user_input_lower or "probability" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["renewal_prob"] = val

    # 7. Entry Yield
    if "entry yield" in user_input_lower or "initial yield" in user_input_lower or "going in yield" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["entry_yield"] = val

    # 8. Capex
    if "capex" in user_input_lower or "capital expenditure" in user_input_lower:
        val = extract_number(user_input_lower)
        if val is not None:
            updated["capex"] = val

    # 9. LTV
    if "ltv" in user_input_lower or "loan to value" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["ltv"] = val

    # 10. Interest Rate
    if "interest" in user_input_lower or "cost of debt" in user_input_lower:
        val = extract_percent(user_input_lower)
        if val is not None:
            updated["interest_rate"] = val

    return updated

def fetch_default_assumptions(asset_type: str = "Logistics") -> dict:
    """
    Simulates fetching default underwriting assumptions from an internal database or API.
    """
    # Mock data
    return {
        "growth": 0.03,
        "erv": 82,
        "exit_yield": 0.0475,
        "discount_rate": 0.065,
        "downtime": 9,
        "renewal_prob": 0.65
    }