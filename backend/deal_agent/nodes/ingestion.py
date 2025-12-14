import os
import json
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from deal_agent.state import DealState
from deal_agent.tools.pdf_parser import parse_pdf_document

# --- Granular Nodes for Real-Time Logging ---

def start_ingestion(state: DealState):
    """
    Step 1: Start Ingestion
    Initializes the process and sends a log message.
    """
    print("--- Node: Start Ingestion ---")
    return {
        "messages": [
            AIMessage(content="Starting data ingestion process...", name="system_log")
        ]
    }

def load_json_data(state: DealState):
    """
    Step 2: Load JSON Data
    Loads the structured JSON file.
    """
    print("--- Node: Load JSON Data ---")
    
    base_dir = os.getcwd()
    if "backend" in base_dir:
        # Already in backend or subdirectory
        # If in backend/, data is in data/
        # If in backend/deal_agent/, data is in ../data/
        # Safest is to find 'backend' and construct path from there
        # But assuming standard execution from root or backend:
        if base_dir.endswith("backend"):
             data_root = os.path.join(base_dir, "data")
        else:
             # Fallback or deeper nesting, try to find relative to file
             current_file_dir = os.path.dirname(os.path.abspath(__file__))
             # .../backend/deal_agent/nodes -> .../backend
             backend_dir = os.path.dirname(os.path.dirname(current_file_dir))
             data_root = os.path.join(backend_dir, "data")
    else:
        # In root, data is in backend/data
        data_root = os.path.join(base_dir, "backend", "data")
        
    json_dir = os.path.join(data_root, "structured_json")
    structured_data = {}
    json_files = []
    
    if os.path.exists(json_dir):
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        if json_files:
            try:
                with open(os.path.join(json_dir, json_files[0]), 'r', encoding='utf-8') as f:
                    structured_data = json.load(f)
            except Exception as e:
                print(f"Error reading JSON: {e}")
                return {
                    "messages": [AIMessage(content=f"Error reading JSON: {e}", name="system_log")]
                }

    msg = f"Loaded structured data from {json_files[0]}" if json_files else "No structured JSON found."
    
    return {
        "messages": [AIMessage(content=msg, name="system_log")],
        "extracted_data": {"source_json": structured_data}
    }

def load_pdf_documents(state: DealState):
    """
    Step 3: Load PDF Documents
    Parses the PDF files.
    """
    print("--- Node: Load PDF Documents ---")
    
    base_dir = os.getcwd()
    if "backend" in base_dir:
        if base_dir.endswith("backend"):
             data_root = os.path.join(base_dir, "data")
        else:
             current_file_dir = os.path.dirname(os.path.abspath(__file__))
             backend_dir = os.path.dirname(os.path.dirname(current_file_dir))
             data_root = os.path.join(backend_dir, "data")
    else:
        data_root = os.path.join(base_dir, "backend", "data")
        
    pdf_dir = os.path.join(data_root, "raw_pdfs")
    pdf_texts = []
    pdf_files = []
    
    if os.path.exists(pdf_dir):
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            try:
                full_path = os.path.join(pdf_dir, pdf_file)
                # Send a log for each file being parsed (optional, or just one summary log)
                # Since we can't stream partial updates easily within a node without custom callback, 
                # we'll just do the work and return the result.
                text = parse_pdf_document.invoke(full_path)
                pdf_texts.append(f"--- Document: {pdf_file} ---\n{text[:10000]}...\n")
            except Exception as e:
                print(f"Error reading PDF {pdf_file}: {e}")

    msg = f"Parsed {len(pdf_files)} PDF documents: {', '.join(pdf_files)}"
    
    # Merge with existing extracted_data
    existing_data = state.get("extracted_data", {})
    existing_data["pdf_texts"] = pdf_texts
    existing_data["pdf_files"] = pdf_files

    return {
        "messages": [AIMessage(content=msg, name="system_log")],
        "extracted_data": existing_data
    }

def align_with_llm(state: DealState):
    """
    Step 4: Align with LLM
    Uses LLM to align JSON and PDF data.
    """
    print("--- Node: Align with LLM ---")
    
    extracted = state.get("extracted_data", {})
    structured_data = extracted.get("source_json", {})
    pdf_texts = extracted.get("pdf_texts", [])
    pdf_files = extracted.get("pdf_files", [])

    if not structured_data and not pdf_texts:
        return {
            "messages": [
                AIMessage(content="No data to align.", name="system_log"),
                AIMessage(content="I could not find any data to process.", name="agent")
            ]
        }

    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    prompt = f"""
    You are an expert Real Estate Investment Analyst.

    I have two data sources:
    1. **Structured Data (JSON)**: This is the source of truth for IDs and basic specs.
    {json.dumps(structured_data, indent=2)[:5000]} 

    2. **Unstructured Data (PDF Content)**:
    {"".join(pdf_texts)}

    **Your Task:**
    1. **Align**: Match the assets in the JSON with the descriptions in the PDF. Use Address or Property Name as the key.
    2. **Extract & Enrich**: For each matched asset, extract the following from the PDF and add it to the data:
       - 'market_highlights': Key selling points of the location.
       - 'investment_rationale': Why is this a good deal?
       - 'risk_factors': Any mentioned risks.
       - 'financials': Extract NOI, ERV, Cap Rate if available.
       - 'physical_specs': Extract Clear Height, Floor Loading, Dock Doors if available.
    3. **Verify**: Check if the GLA (Gross Leasable Area) and Occupancy in the JSON match the PDF. If different, create a 'discrepancies' field.

    Return a summary of the aligned deal data in a readable format for the user, highlighting the key metrics and any discrepancies found.
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    status_msg = "Alignment complete. Generating summary..."
    
    # Update extracted data with analysis
    extracted["analysis"] = response.content

    return {
        "messages": [
            AIMessage(content=status_msg, name="system_log"),
            AIMessage(content=response.content, name="agent")
        ],
        "extracted_data": extracted
    }

def compute_metrics_and_draft_summary(state: DealState):
    """
    Step 5: Compute Metrics and Draft Summary
    Reads initial data and computes preliminary summaries.
    """
    print("--- Node: Compute Metrics and Draft Summary ---")

    extracted = state.get("extracted_data", {})
    source_json = extracted.get("source_json", {})
    analysis_text = extracted.get("analysis", "")

    if not source_json and not analysis_text:
        return {"messages": [AIMessage(content="No data available to compute metrics.", name="agent")]}

    # Use LLM to synthesize metrics from the ingested data
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)

    prompt = f"""
    You are a Real Estate Analyst. 
    Based on the provided structured data and the analysis from the ingestion step, generate a concise "Metrics Summary".

    **Source Data (JSON):**
    {json.dumps(source_json, indent=2)[:2000]}

    **Preliminary Analysis:**
    {analysis_text}

    **Task:**
    Compute or extract the following key metrics. If a value is not explicitly available, estimate it from the context or mark as "TBD".

    **Output Format:**
    Compute Metrics and Draft Summary:
    - Total GLA: [Value + Unit]
    - Occupancy: [Value %]
    - WALT: [Value Years]
    - In-Place Rent: [Value / sqft or sqm]
    - [Add any other relevant high-level metric found]
    """

    response = llm.invoke([HumanMessage(content=prompt)])

    return {"messages": [AIMessage(content=response.content, name="agent")]}
