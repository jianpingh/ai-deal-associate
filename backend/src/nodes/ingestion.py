from langchain_core.messages import AIMessage
from src.state import DealState

def ingest_and_align(state: DealState):
    """
    Step 1: Ingest and Align
    Parses uploaded documents (IM, rent roll, JSON) and aligns entities.
    """
    print("--- Node: Ingest and Align ---")
    
    # Status update simulating the system actions
    status_content = (
        "System Processing:\n"
        "- Loads IM, rent roll, and other PDFs\n"
        "- Loads structured JSON (assets, leases, logistics specs)\n"
        "- Aligns PDFs with structured entities"
    )
    
    # Agent response
    response_content = (
        "I’ve ingested the IM, rent roll and structured deal data.\n\n"
        "I’ll generate the summary, key metrics, and an initial set of comparables."
    )
    
    return {
        "messages": [
            AIMessage(content=status_content),
            AIMessage(content=response_content)
        ],
        "extracted_data": {"status": "done", "property_name": "Logistics Hub North"}
    }

def compute_metrics_and_draft_summary(state: DealState):
    """
    Step 2: Compute Metrics and Draft Summary
    Reads initial data and computes preliminary summaries.
    """
    print("--- Node: Compute Metrics and Draft Summary ---")
    
    # Simulate computed metrics
    metrics_summary = (
        "Compute Metrics and Draft Summary:\n"
        "- Total GLA: 250,000 sqft\n"
        "- Occupancy: 95%\n"
        "- WALT: 4.2 Years\n"
        "- In-Place Rent: $12.50 psf"
    )
    
    return {"messages": [AIMessage(content=metrics_summary)]}

def ingestion_node(state: DealState):
    # Legacy
    pass

