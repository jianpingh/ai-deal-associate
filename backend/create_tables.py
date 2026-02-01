"""
Create all database tables in PostgreSQL

Run: python create_tables.py
"""

import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

# Import models first to register them
print("Loading models...")
from db.models.user import User
from db.models.deal import Deal
from db.models.asset import Asset
from db.models.document import Document
from db.models.tenant import Tenant
from db.models.comparable import Comparable
from db.models.market_data import MarketData
from db.models.assumption import Assumption
from db.models.financial_model import FinancialModel
from db.models.cashflow_projection import CashflowProjection
from db.models.sensitivity_analysis import SensitivityAnalysis
from db.models.scenario import Scenario
from db.models.loan_quote import LoanQuote
from db.models.rent_roll import RentRoll
from db.models.operating_statement import OperatingStatement
from db.models.deck_version import DeckVersion
from db.models.chat_thread import ChatThread
from db.models.chat_message import ChatMessage
from db.models.deal_team import DealTeam
from db.models.audit_log import AuditLog
from db.models.notification import Notification
from db.models.template import Template

# Now import database engine
from sqlmodel import SQLModel
from db.database import engine

if __name__ == "__main__":
    if engine is None:
        print("ERROR: DATABASE_URL not configured")
        sys.exit(1)
    
    print("Creating all tables...")
    SQLModel.metadata.create_all(engine)
    print("✅ All tables created successfully!")
    
    # List all tables
    print("\nTables created:")
    for table_name in sorted(SQLModel.metadata.tables.keys()):
        print(f"  - {table_name}")
