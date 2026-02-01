"""
Sensitivity Analysis Model
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON


class SensitivityAnalysis(SQLModel, table=True):
    """Sensitivity analysis matrix database model"""
    __tablename__ = "sensitivity_analyses"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: int = Field(index=True)  # FK → financial_models
    
    # Analysis type
    analysis_name: str = Field(default="IRR Sensitivity")
    output_metric: str = Field(default="irr")  # irr, equity_multiple, npv
    
    # X-axis variable
    variable_x: str  # e.g., "exit_cap_rate"
    variable_x_label: Optional[str] = None  # e.g., "Exit Cap Rate"
    values_x: list = Field(sa_column=Column(JSON))  # [4.5, 5.0, 5.5, 6.0, 6.5]
    
    # Y-axis variable
    variable_y: str  # e.g., "rent_growth_rate"
    variable_y_label: Optional[str] = None  # e.g., "Rent Growth"
    values_y: list = Field(sa_column=Column(JSON))  # [2.0, 2.5, 3.0, 3.5, 4.0]
    
    # Result matrix
    # 2D array: matrix_data[y_index][x_index] = result value
    matrix_data: list = Field(sa_column=Column(JSON))
    # Example: [[15.2, 14.5, 13.8], [16.1, 15.4, 14.7], ...]
    
    # Base case position in matrix (for highlighting)
    base_case_x_index: Optional[int] = None
    base_case_y_index: Optional[int] = None
    base_case_value: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
