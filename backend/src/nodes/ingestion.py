from src.state import DealState

def ingest_and_align(state: DealState):
    """
    Step 1: Ingest and Align
    Parses uploaded documents (IM, rent roll, JSON) and aligns entities.
    """
    print("--- Node: Ingest and Align ---")
    # Placeholder logic
    return {"messages": ["Ingestion and alignment complete."], "extracted_data": {"status": "done"}}

def compute_metrics_and_draft_summary(state: DealState):
    """
    Step 2: Compute Metrics and Draft Summary
    Reads initial data and computes preliminary summaries.
    """
    print("--- Node: Compute Metrics and Draft Summary ---")
    # Placeholder logic
    return {"messages": ["Metrics computed and summary drafted."]}

def ingestion_node(state: DealState):
    # Legacy
    pass

