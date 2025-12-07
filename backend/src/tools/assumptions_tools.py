import re

def process_assumption_updates(current_assumptions: dict, user_input: str) -> dict:
    """
    Parses user input to update financial assumptions.
    Supports updates for: growth, exit yield, discount rate, ERV, downtime, renewal probability.
    """
    updated = current_assumptions.copy()
    user_input_lower = user_input.lower()

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

    return updated
