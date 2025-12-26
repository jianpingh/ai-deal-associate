import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def process_assumption_updates(current_assumptions: dict, user_input: str) -> dict:
    """
    Parses user input to update financial assumptions using LLM for semantic understanding.
    Supports updates for: growth, exit yield, discount rate, ERV, downtime, renewal probability, etc.
    """
    updated = current_assumptions.copy()
    
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        # Define the schema and instructions for the LLM
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are a financial modeling assistant. Your task is to update financial assumptions based on the user's input.\n"
             "Current Assumptions: {current_assumptions}\n\n"
             "Instructions:\n"
             "1. Identify which assumptions the user wants to change.\n"
             "2. Extract the new values. Convert percentages to decimals (e.g., 5% -> 0.05).\n"
             "3. Return a JSON object containing ONLY the keys that need to be updated.\n"
             "4. Supported keys: 'erv' (Market Rent), 'growth' (Rent Growth), 'exit_yield', 'entry_yield', 'discount_rate', "
             "'downtime' (months), 'renewal_prob' (probability), 'ltv', 'interest_rate', 'capex', 'opex_ratio'.\n"
             "5. If the user says 'increase by X', calculate the new value based on the current assumption.\n"
             "6. If the user says 'set to X', use X directly.\n"
             "7. For ERV/Rent, if the user gives a value like '100', assume it's the absolute value. If they say '+10%', calculate it.\n"
             "8. Do not include markdown formatting like ```json."
            ),
            ("user", "{user_input}")
        ])
        
        chain = prompt | llm | JsonOutputParser()
        
        # Invoke the chain
        changes = chain.invoke({
            "current_assumptions": current_assumptions,
            "user_input": user_input
        })
        
        # Apply changes to the updated dictionary
        if isinstance(changes, dict):
            for key, value in changes.items():
                if key in updated:
                    # Type safety checks
                    if key in ['downtime']:
                        updated[key] = int(value)
                    else:
                        updated[key] = float(value)
                else:
                    # Allow adding new keys if they are valid assumption keys
                    valid_keys = ['erv', 'growth', 'exit_yield', 'entry_yield', 'discount_rate', 
                                  'downtime', 'renewal_prob', 'ltv', 'interest_rate', 'capex', 'opex_ratio']
                    if key in valid_keys:
                         updated[key] = float(value)
                         
    except Exception as e:
        print(f"[WARNING] LLM assumption parsing failed: {e}. Falling back to regex.")
        # Fallback to original regex logic if LLM fails
        return _process_assumption_updates_regex(updated, user_input)

    return updated

def _process_assumption_updates_regex(current_assumptions: dict, user_input: str) -> dict:
    """
    Fallback regex-based parser.
    """
    updated = current_assumptions.copy()
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