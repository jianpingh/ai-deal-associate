from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class DealState(TypedDict):
    """
    State definition for the AI Deal Associate.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Context data
    current_deal_id: Optional[str]
    company_name: Optional[str]
    industry: Optional[str]
    
    # Process tracking (mapping to the 18 processes)
    current_process_step: Optional[str]
    
    # Data storage
    extracted_data: Dict[str, Any]  # From PDF ingestion
    comps_data: List[Dict[str, Any]] # Comparable companies
    financial_assumptions: Dict[str, Any]
    financial_model: Dict[str, Any] # Calculated model results
    deck_content: Dict[str, Any] # Generated deck structure
    scenarios: Dict[str, Any] # Scenario analysis results
