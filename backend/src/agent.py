from typing import Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from src.state import DealState
from src.nodes import (
    ingestion,
    comps,
    assumptions,
    model,
    deck,
    scenarios,
    chatbot,
    human_interaction
)

# Load environment variables
load_dotenv()

# --- LLM Setup -------------------------------------------------------------
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- Intent Router ---------------------------------------------------------
class Intent(BaseModel):
    action: Literal["ingest", "comps", "assumptions", "model", "deck", "scenarios", "chat"] = Field(
        ..., 
        description=(
            "Classify the user's intent into a workflow action or general chat.\n"
            "- 'ingest': Start deal, underwriting, upload documents (e.g., 'Start underwriting').\n"
            "- 'comps': Comparables, market research, competitors (e.g., 'Show comps', 'Remove Comp A').\n"
            "- 'assumptions': Financial assumptions, growth rates, caps (e.g., 'What are assumptions', 'Change growth to 3%').\n"
            "- 'model': Build model, calculate IRR/valuation (e.g., 'Build model').\n"
            "- 'deck': Generate presentation, memo, summary (e.g., 'Generate deck').\n"
            "- 'scenarios': Scenario analysis, sensitivity, stress test (e.g., 'Run downside case').\n"
            "- 'chat': General conversation, greetings, clarifications, or feedback not triggering a specific step."
        )
    )

def intent_router_node(state: DealState):
    print("--- Node: Intent Router ---")
    
    system_message = """You are an AI Deal Associate routing user requests.
    
    Determine if the user's message is a request to perform a specific workflow action (Workflow) or a general question/comment (Chat).
    
    Workflow Actions:
    - ingest: Start new deal, upload documents, begin underwriting.
    - comps: View, propose, modify, or update comparables.
    - assumptions: View, propose, modify, or update financial assumptions.
    - model: Build, rebuild, or calculate the financial model.
    - deck: Generate, create, or update the presentation deck/memo.
    - scenarios: Run scenario analysis, stress tests, or sensitivity analysis.
    
    Chat:
    - General questions about the property or market.
    - Clarifications that don't require changing the deal state.
    - Greetings or off-topic.
    """
    
    # Construct the prompt messages
    prompt = [SystemMessage(content=system_message)] + state["messages"]
    
    structured_llm = llm.with_structured_output(Intent)
    try:
        intent = structured_llm.invoke(prompt)
        return {"current_process_step": intent.action}
    except Exception as e:
        print(f"Intent routing failed: {e}")
        return {"current_process_step": "chat"}

def route_intent(state: DealState):
    intent = state.get("current_process_step", "chat")
    
    # --- Dependency Checks (Strict Workflow Enforcement) ---
    # Map intents to the data they require to proceed.
    # If the data is missing, we must go to the step that produces it.
    requirements = {
        "scenarios": "financial_model",
        "deck": "financial_model",
        "model": "financial_assumptions",
        "assumptions": "comps_data",
        "comps": "extracted_data"
    }
    
    # Map data to the step that produces it (Fallback targets)
    producers = {
        "financial_model": "model",
        "financial_assumptions": "assumptions",
        "comps_data": "comps",
        "extracted_data": "ingest"
    }
    
    target = intent
    
    # Iteratively check dependencies to find the earliest missing step
    # This avoids duplicate code paths and ensures strict order.
    for _ in range(10): # Safety limit
        if target in requirements:
            req_data = requirements[target]
            # Check if the required data exists in state
            if not state.get(req_data):
                # Missing dependency, fallback to the producer step
                target = producers[req_data]
            else:
                # Dependency met, stop checking
                break
        else:
            # No dependencies (e.g. ingest, chat), stop checking
            break

    # --- Routing Map ---
    mapping = {
        "ingest": "ingest_and_align",
        "comps": "propose_comparables",
        "assumptions": "propose_assumptions",
        "model": "build_model",
        "deck": "generate_deck",
        "scenarios": "prepare_scenario_analysis",
        "chat": "chatbot"
    }
    
    return mapping.get(target, "chatbot")

# --- Graph Definition ------------------------------------------------------
workflow = StateGraph(DealState)

# Add Nodes
workflow.add_node("intent_router", intent_router_node)
workflow.add_node("chatbot", chatbot.chatbot_node)

# Ingestion
workflow.add_node("ingest_and_align", ingestion.ingest_and_align)
workflow.add_node("compute_metrics_and_draft_summary", ingestion.compute_metrics_and_draft_summary)

# Comps
workflow.add_node("propose_comparables", comps.propose_comparables)
workflow.add_node("human_review_comps", human_interaction.human_review_comps) # Step 4
workflow.add_node("update_comparables", comps.update_comparables)

# Assumptions
workflow.add_node("propose_assumptions", assumptions.propose_assumptions)
workflow.add_node("human_review_assumptions", human_interaction.human_review_assumptions) # Step 7
workflow.add_node("update_assumptions", assumptions.update_assumptions)

# Model
workflow.add_node("human_confirm_model_build", human_interaction.human_confirm_model_build) # Step 9
workflow.add_node("build_model", model.build_model)

# Deck
workflow.add_node("human_confirm_deck_generation", human_interaction.human_confirm_deck_generation) # Step 11
workflow.add_node("generate_deck", deck.generate_deck)
workflow.add_node("refresh_deck_views", deck.refresh_deck_views)

# Scenarios
workflow.add_node("prepare_scenario_analysis", scenarios.prepare_scenario_analysis)
workflow.add_node("wait_for_scenario_requests", human_interaction.wait_for_scenario_requests) # Step 14
workflow.add_node("apply_scenario", scenarios.apply_scenario)
workflow.add_node("rebuild_model_for_scenario", scenarios.rebuild_model_for_scenario)
workflow.add_node("wait_for_more_scenarios", scenarios.wait_for_more_scenarios)

# --- Edges -----------------------------------------------------------------
workflow.set_entry_point("intent_router")

workflow.add_conditional_edges(
    "intent_router",
    route_intent,
    {
        "ingest_and_align": "ingest_and_align",
        "propose_comparables": "propose_comparables",
        "propose_assumptions": "propose_assumptions",
        "build_model": "build_model",
        "generate_deck": "generate_deck",
        "prepare_scenario_analysis": "prepare_scenario_analysis",
        "chatbot": "chatbot"
    }
)

workflow.add_edge("chatbot", END)

# Ingestion Flow
workflow.add_edge("ingest_and_align", "compute_metrics_and_draft_summary")
workflow.add_edge("compute_metrics_and_draft_summary", END)

# Comps Flow
workflow.add_edge("propose_comparables", "human_review_comps")
workflow.add_edge("human_review_comps", "update_comparables")
workflow.add_edge("update_comparables", END)

# Assumptions Flow
workflow.add_edge("propose_assumptions", "human_review_assumptions")
workflow.add_edge("human_review_assumptions", "update_assumptions")
workflow.add_edge("update_assumptions", "human_confirm_model_build") # Flow into model prep

# Model Flow
workflow.add_edge("human_confirm_model_build", "build_model")
workflow.add_edge("build_model", "human_confirm_deck_generation") # Flow into deck prep

# Deck Flow
workflow.add_edge("human_confirm_deck_generation", "generate_deck")
workflow.add_edge("generate_deck", END)

# Scenarios Flow
workflow.add_edge("prepare_scenario_analysis", "wait_for_scenario_requests")
workflow.add_edge("wait_for_scenario_requests", "apply_scenario")
workflow.add_edge("apply_scenario", "rebuild_model_for_scenario")
workflow.add_edge("rebuild_model_for_scenario", "refresh_deck_views")
workflow.add_edge("refresh_deck_views", "wait_for_more_scenarios")
workflow.add_edge("wait_for_more_scenarios", "prepare_scenario_analysis") # Loop

# --- Compile ---------------------------------------------------------------
app = workflow.compile(
    interrupt_before=[
        "update_comparables",       # Step 5: Interrupt after human_review_comps
        "update_assumptions",       # Step 8: Interrupt after human_review_assumptions
        "build_model",              # Step 10: Interrupt after human_confirm_model_build
        "generate_deck",            # Step 12: Interrupt after human_confirm_deck_generation
        "apply_scenario",           # Step 15: Interrupt after wait_for_scenario_requests
        "wait_for_more_scenarios"   # Step 18: Loop interrupt
    ]
)
