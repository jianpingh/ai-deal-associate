from langgraph.graph import StateGraph, END
from src.state import DealState
from src.nodes import (
    ingestion,
    comps,
    assumptions,
    model,
    deck,
    scenarios,
    chatbot
)

# Define the graph
workflow = StateGraph(DealState)

# Add nodes
# These nodes correspond to the high-level logic blocks which contain the 18 processes
workflow.add_node("chatbot", chatbot.chatbot_node)
workflow.add_node("ingestion", ingestion.ingestion_node)
workflow.add_node("comps", comps.comps_node)
workflow.add_node("assumptions", assumptions.assumptions_node)
workflow.add_node("model", model.model_node)
workflow.add_node("deck", deck.deck_node)
workflow.add_node("scenarios", scenarios.scenarios_node)

# Define edges
# This is a simplified flow. In a real application, the router would be more complex.
workflow.set_entry_point("chatbot")

workflow.add_edge("chatbot", END) # Default to end if no specific action needed
# Add conditional edges based on intent detected in chatbot node
# workflow.add_conditional_edges(
#     "chatbot",
#     chatbot.route_intent,
#     {
#         "ingest": "ingestion",
#         "comps": "comps",
#         "model": "model",
#         "deck": "deck",
#         "scenarios": "scenarios",
#         "end": END
#     }
# )

# Compile the graph
app = workflow.compile()
