"""
Database Models

SQLModel ORM models for database tables.
"""

# Core entities
from .user import User
from .deal import Deal
from .asset import Asset
from .document import Document
from .tenant import Tenant

# Comparables & Market
from .comparable import Comparable
from .market_data import MarketData

# Financial
from .assumption import Assumption
from .financial_model import FinancialModel
from .cashflow_projection import CashflowProjection
from .sensitivity_analysis import SensitivityAnalysis
from .scenario import Scenario
from .loan_quote import LoanQuote

# Property data
from .rent_roll import RentRoll
from .operating_statement import OperatingStatement

# Outputs
from .deck_version import DeckVersion

# Chat
from .chat_thread import ChatThread
from .chat_message import ChatMessage

# Analysis (legacy)
from .analysis import Analysis
from .chat import ChatHistory

# Collaboration & Admin
from .deal_team import DealTeam
from .notification import Notification
from .audit_log import AuditLog
from .template import Template


__all__ = [
    # Core
    "User",
    "Deal",
    "Asset",
    "Document",
    "Tenant",
    
    # Comparables & Market
    "Comparable",
    "MarketData",
    
    # Financial
    "Assumption",
    "FinancialModel",
    "CashflowProjection",
    "SensitivityAnalysis",
    "Scenario",
    "LoanQuote",
    
    # Property data
    "RentRoll",
    "OperatingStatement",
    
    # Outputs
    "DeckVersion",
    
    # Chat
    "ChatThread",
    "ChatMessage",
    
    # Legacy
    "Analysis",
    "ChatHistory",
    
    # Collaboration & Admin
    "DealTeam",
    "Notification",
    "AuditLog",
    "Template",
]
