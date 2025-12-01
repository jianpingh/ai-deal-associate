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
│   ├── src/
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
│   │   │   └── chatbot.py          # General Chat & Intent Recognition
│   │   ├── tools/                  # [Tools] Underlying Capabilities
│   │   │   ├── __init__.py
│   │   │   ├── pdf_parser.py       # PDF Parsing (Unstructured/Azure)
│   │   │   ├── rag_tools.py        # Vector Retrieval (Pinecone)
│   │   │   ├── excel_engine.py     # Excel Operations (openpyxl)
│   │   │   └── ppt_engine.py       # PPT Operations (python-pptx)
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

## 18 Processes & Node Mapping

The AI Deal Associate is designed to handle 18 key processes in the M&A deal lifecycle. These processes are mapped to specific nodes in the LangGraph architecture.

| Node File | Node Name | Corresponding Processes | Description |
|-----------|-----------|-------------------------|-------------|
| `ingestion.py` | `ingestion` | 1. NDA Processing<br>2. CIM Ingestion<br>3. Financial Spreading (Historical) | Handles the intake of documents (PDFs, Excel) and extracts structured data. |
| `comps.py` | `comps` | 4. Competitor Analysis<br>5. Precedent Transactions<br>6. Market Research | Searches for and analyzes comparable companies and transactions. |
| `assumptions.py` | `assumptions` | 7. Revenue Projections<br>8. Cost Projections<br>9. Macro Assumptions | Generates financial assumptions based on historical data and market trends. |
| `model.py` | `model` | 10. DCF Modeling<br>11. LBO Modeling<br>12. Valuation Summary | Performs complex financial calculations and model updates. |
| `scenarios.py` | `scenarios` | 13. Sensitivity Analysis<br>14. Stress Testing | Runs various scenarios (Base, Bull, Bear) to test valuation resilience. |
| `deck.py` | `deck` | 15. Teaser Generation<br>16. Investment Memo Drafting<br>17. Management Presentation | Generates PowerPoint slides and documents based on analysis. |
| `chatbot.py` | `chatbot` | 18. Q&A / Due Diligence Support | Handles ad-hoc queries, buyer list generation, and general interaction. |

*(Note: Processes like Company Profiling and Buyer List Generation are also handled via the Chatbot and RAG tools)*

## Getting Started

### Prerequisites

- Python 3.11+
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
