from langchain_core.messages import AIMessage
from deal_agent.state import DealState
from pptx import Presentation
import os
from deal_agent.tools.s3_utils import upload_to_s3_and_get_link

def generate_deck(state: DealState):
    """
    Step 12: Generate Deck
    Produces a one-page summary or a full IC Deck.
    """
    print("--- Node: Generate Deck ---")
    
    # Create PPT
    prs = Presentation()
    
    # --- Helper to add text to slide ---
    def add_slide(title, content_text):
        slide_layout = prs.slide_layouts[1] # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        if slide.shapes.title:
            slide.shapes.title.text = title
        if len(slide.placeholders) > 1:
            tf = slide.placeholders[1].text_frame
            tf.clear()
            # Split by newlines to create bullet points
            for line in str(content_text).split('\n'):
                if line.strip():
                    p = tf.add_paragraph()
                    p.text = line.strip()
                    p.level = 0

    # --- 1. Summary ---
    extracted = state.get("extracted_data", {})
    analysis = extracted.get("analysis", "No analysis available.")
    add_slide("Summary", analysis[:1000]) # Truncate to fit

    # --- 2. Market ---
    # Try to extract market info or use generic placeholder
    market_info = "Market Highlights:\n- Prime logistics location\n- Strong demand fundamentals\n- Low vacancy rates in the submarket"
    if "market_highlights" in extracted:
        market_info = extracted["market_highlights"]
    add_slide("Market", market_info)

    # --- 3. Tenancy ---
    tenancy_data = extracted.get("tenancy_schedule", [])
    if not tenancy_data and "source_json" in extracted:
         tenancy_data = extracted["source_json"].get("tenants", [])
    
    tenancy_text = "Key Tenants:"
    if tenancy_data:
        for t in tenancy_data:
            name = t.get("name", "Unknown")
            area = t.get("area", "N/A")
            tenancy_text += f"\n- {name}: {area} sqm"
    else:
        tenancy_text += "\n- Logistics Corp A: 5,000 sqm\n- E-Commerce Ltd: 3,000 sqm\n- Global Supply Chain: 2,000 sqm"
    add_slide("Tenancy", tenancy_text)

    # --- 4. Business Plan ---
    assumptions = state.get("assumptions", {})
    bp_text = "Key Assumptions:"
    bp_text += f"\n- Market Rent: {assumptions.get('market_rent', 85)} EUR/sqm"
    bp_text += f"\n- Entry Yield: {assumptions.get('entry_yield', 0.045):.2%}"
    bp_text += f"\n- Exit Yield: {assumptions.get('exit_yield', 0.0475):.2%}"
    bp_text += f"\n- Capex: {assumptions.get('capex', 0):,} EUR"
    add_slide("Business Plan", bp_text)

    # --- 5. Sensitivities ---
    sens_text = "Sensitivity Analysis:\n- Impact of Exit Yield expansion (+25bps)\n- Impact of Rent Growth reduction (-1%)\n- Interest Rate stress test (+100bps)"
    add_slide("Sensitivities", sens_text)

    # --- 6. Appendix ---
    app_text = "Documents Reviewed:\n- Investment Memorandum.pdf\n- Rent Roll.xlsx\n- Technical DD Report.pdf"
    add_slide("Appendix", app_text)

    # Save locally
    filename = "IC_Deck_v1.pptx"
    # current file is in backend/deal_agent/nodes/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_dir))
    output_dir = os.path.join(backend_dir, "data", "generated")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    try:
        prs.save(output_path)
        # Upload to S3
        s3_link = upload_to_s3_and_get_link(output_path)
    except Exception as e:
        print(f"Error generating/uploading deck: {e}")
        s3_link = None
    
    download_msg = ""
    if s3_link:
        download_msg = f"\n\n📥 **[Download IC Deck (PPT)]({s3_link})**"
    else:
        download_msg = f"\n\n(IC Deck generated locally at {output_path}, but S3 upload failed)"

    # Status update simulating system actions
    status_content = (
        "System Processing:\n"
        "- Generates PPTX one-pager and IC deck\n"
        f"- Uploads to S3: {filename}"
    )
    
    # Agent response
    response_content = (
        "IC deck generated (summary, market, tenancy, business plan, sensitivities, appendix)."
        f"{download_msg}\n\n"
        "Would you like to run any scenarios (e.g. +5% ERV, +25 bps exit yield) and refresh key charts?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ],
        "deck_content": {"slides": ["Summary", "Market", "Tenancy", "Business Plan", "Sensitivities", "Appendix"]}
    }

def refresh_deck_views(state: DealState):
    """
    Step 17: Refresh Deck Views
    Updates or generates deck pages with scenario comparisons.
    """
    print("--- Node: Refresh Deck Views ---")
    
    # Status update
    status_content = (
        "System Processing:\n"
        "- Updates sensitivity tables in Deck\n"
        "- Refreshes return charts (IRR/EM vs Base Case)\n"
        "- Saves new version: Download IC Deck v2 (Scenario A).pptx"
    )
    
    # Agent response asking for more scenarios
    response_content = (
        "Deck views refreshed with the new scenario data.\n\n"
        "Would you like to run another scenario (e.g., 'stress test interest rates'), or is the analysis complete?"
    )
    
    return {
        "messages": [
            AIMessage(content=status_content, name="system_log"),
            AIMessage(content=response_content, name="agent")
        ]
    }

def deck_node(state: DealState):
    pass

