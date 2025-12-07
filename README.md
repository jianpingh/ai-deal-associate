# AI Deal Associate

An AI-powered agent designed to assist with M&A deal processes, built with LangGraph (Backend) and Next.js (Frontend).

## Project Structure

The project is organized into a backend service and a frontend application.

```
ai-deal-associate/
├── .github/                        # CI/CD Configuration
│   └── workflows/
│       ├── deploy-frontend.yml     # Auto deploy frontend to Vercel
│       └── deploy-backend.yml      # Auto deploy backend to LangGraph Cloud
├── backend/                        # Backend (Python / LangGraph)
│   ├── deal_agent/
│   │   ├── __init__.py
│   │   ├── agent.py                # [Core] Graph Definition & Compilation
│   │   ├── state.py                # [State] DealState Definition
│   │   ├── nodes/                  # [Nodes] Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── ingestion.py        # Ingestion & Alignment
│   │   │   ├── comps.py            # Comparable Case Logic
│   │   │   ├── assumptions.py      # Assumption Generation Logic
│   │   │   ├── model.py            # Financial Model Calculation
│   │   │   ├── deck.py             # PPT Generation
│   │   │   ├── scenarios.py        # Scenario Analysis
│   │   │   ├── chatbot.py          # General Chat & Intent Recognition
│   │   │   └── human_interaction.py # Human-in-the-loop Logic
│   │   ├── tools/                  # [Tools] Underlying Capabilities
│   │   │   ├── __init__.py
│   │   │   ├── pdf_parser.py       # PDF Parsing (Unstructured/Azure)
│   │   │   ├── rag_tools.py        # Vector Retrieval (Pinecone)
│   │   │   ├── excel_engine.py     # Excel Operations (openpyxl)
│   │   │   ├── ppt_engine.py       # PPT Operations (python-pptx)
│   │   │   ├── comps_financial_calcs.py # Financial Math
│   │   │   └── assumptions_tools.py # Assumption Parsing
│   │   └── utils/                  # [Common] Config & Logging
│   │       ├── config.py
│   │       └── logger.py
│   ├── tests/                      # Unit Tests
│   ├── .env                        # Local Environment Variables
│   ├── .gitignore
│   ├── Dockerfile                  # Container Configuration
│   ├── langgraph.json              # LangGraph Cloud Config File
│   └── requirements.txt            # Python Dependencies
├── frontend/                       # Frontend (Next.js / TypeScript)
│   ├── app/                        # App Router
│   │   ├── page.tsx                # Main Chat Page
│   │   ├── layout.tsx              # Global Layout
│   │   └── globals.css             # Tailwind Styles
│   ├── components/                 # UI Components
│   │   ├── chat/                   # Chat Bubbles, Input Box
│   │   ├── deal/                   # Business Components (CompsTable, ModelView)
│   │   └── ui/                     # Basic Components (Button, Card)
│   ├── lib/                        # Utility Libraries
│   │   ├── client.ts               # LangGraph SDK Client
│   │   └── types.ts                # Type Definitions
│   ├── public/                     # Static Resources
│   ├── .env.local                  # Frontend Environment Variables
│   ├── next.config.js
│   ├── package.json
│   └── tsconfig.json
├── data/                           # Local Test Data (Not Uploaded)
│   ├── raw_pdfs/
│   ├── structured_json/
│   └── templates/                  # Excel/PPT Template Files
└── README.md                       # Project Documentation
```

## Workflow Nodes & Integration

The AI Deal Associate is designed to handle key processes in the M&A deal lifecycle. These processes are mapped to specific nodes in the LangGraph architecture.

| **Step** | **Node Name** (`node_name`) | **Description** | **Interrupt?** | **Next Step** |
| :--- | :--- | :--- | :--- | :--- |
| **Entry** | `intent_router` | **Core Routing Logic**: Analyzes user input using LLM to determine the intent (e.g., ingest, comps, model) and checks dependencies (e.g., cannot build model without assumptions). | No | *Dynamic* (Based on Intent) |
| **Chat** | [`chatbot`](backend/deal_agent/nodes/chatbot.py) | Handles general conversation, greetings, or requests that don't trigger a workflow action. | **END** | (Wait for user) |
| **Ingest** | [`ingest_and_align`](backend/deal_agent/nodes/ingestion.py) | **Step 1**: Parses uploaded documents (PDFs, Excel) and structured JSON data. Aligns unstructured data with deal entities. | No | `compute_metrics...` |
| | `compute_metrics...` | **Step 2**: Computes preliminary metrics (GLA, WALT, Occupancy) from the ingested data and drafts a deal summary. | No | [`propose_comparables`](backend/deal_agent/nodes/comps.py) |
| **Comps** | [`propose_comparables`](backend/deal_agent/nodes/comps.py) | **Step 3**: Searches the database for relevant comparable assets based on location, size, and type. Calculates initial blended market rent. | No | [`human_review_comps`](backend/deal_agent/nodes/human_interaction.py) |
| | [`human_review_comps`](backend/deal_agent/nodes/human_interaction.py) | **Step 4**: Presents the proposed comparables to the user and waits for feedback. | **END** | (Wait for user) |
| | [`update_comparables`](backend/deal_agent/nodes/comps.py) | **Step 5**: **Interactive Update**: Parses user requests (e.g., "Remove Comp A", "Add Comp D") to modify the comps list and recalculate market rent. | No | **END** |
| **Assumptions** | [`propose_assumptions`](backend/deal_agent/nodes/assumptions.py) | **Step 6**: Drafts financial assumptions (ERV, Yield, Growth, Downtime) based on the finalized comps and tenancy schedule. | No | [`human_review_assumptions`](backend/deal_agent/nodes/human_interaction.py) |
| | [`human_review_assumptions`](backend/deal_agent/nodes/human_interaction.py) | **Step 7**: Presents the proposed assumptions to the user and waits for feedback. | **END** | (Wait for user) |
| | [`update_assumptions`](backend/deal_agent/nodes/assumptions.py) | **Step 8**: **Interactive Update**: Parses user requests (e.g., "Change growth to 3%") to update specific financial assumptions. | No | **END** |
| **Model** | [`human_confirm_model_build`](backend/deal_agent/nodes/human_interaction.py) | **Step 9**: Asks the user for final confirmation before building the complex financial model. | **END** | (Wait for user) |
| | [`build_model`](backend/deal_agent/nodes/model.py) | **Step 10**: **Core Calculation**: Fills the Excel template with data and assumptions. Calculates IRR, Equity Multiple, and Yield on Cost. | No | `human_confirm_deck...` |
| **Deck** | `human_confirm_deck...` | **Step 11**: Asks the user for confirmation to generate the Investment Committee (IC) presentation deck. | **END** | (Wait for user) |
| | [`generate_deck`](backend/deal_agent/nodes/deck.py) | **Step 12**: Generates a PowerPoint presentation (or Memo) summarizing the deal, market, valuation, and business plan. | **END** | (Wait for user) |
| | [`refresh_deck_views`](backend/deal_agent/nodes/deck.py) | **Step 13**: Updates specific slides/charts in the deck after a scenario analysis run. | **END** | (Wait for user) |
| **Scenarios** | [`prepare_scenario_analysis`](backend/deal_agent/nodes/scenarios.py) | **Step 14**: Initializes the scenario analysis environment. | No | `wait_for_scenario...` |
| | `wait_for_scenario...` | **Step 15**: Prompts the user to define a scenario (e.g., "Run downside case with -5% rent"). | **END** | (Wait for user) |
| | [`apply_scenario`](backend/deal_agent/nodes/scenarios.py) | **Step 16**: Parses the scenario parameters and applies them to the financial model. | No | `rebuild_model...` |
| | `rebuild_model...` | **Step 17**: Re-runs the financial model with the new scenario parameters. | No | [`refresh_deck_views`](backend/deal_agent/nodes/deck.py) |
| | [`wait_for_more_scenarios`](backend/deal_agent/nodes/scenarios.py) | **Step 18**: (Optional Loop) Asks if the user wants to run additional scenarios. | No | `prepare_scenario...` |

*(Note: Processes like Company Profiling and Buyer List Generation are also handled via the Chatbot and RAG tools)*

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   Copy `.env.example` to `.env` (if available) or create `.env` with your API keys (OpenAI, Pinecone, LangSmith).
4. Run the server:
   ```bash
   uvicorn src.agent:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Deployment

- **Frontend**: Automatically deployed to Vercel via GitHub Actions.
- **Backend**: Automatically deployed to LangGraph Cloud via GitHub Actions.

## License

[License Name]
