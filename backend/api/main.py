from fastapi import FastAPI, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

# Import database session and models
# Note: In a real project, use absolute imports assuming 'backend' is in PYTHONPATH check logic
# But for typical simplified structure inside backend/:
from api.database import get_session
from api.models import Deal, Asset

app = FastAPI(title="AI Deal Associate API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Deal Associate API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# --- Deal Endpoints ---

@app.post("/deals/", response_model=Deal)
def create_deal(deal: Deal, session: Session = Depends(get_session)):
    session.add(deal)
    session.commit()
    session.refresh(deal)
    return deal

@app.get("/deals/", response_model=List[Deal])
def read_deals(
    offset: int = 0, 
    limit: int = Query(default=100, le=100), 
    session: Session = Depends(get_session)
):
    deals = session.exec(select(Deal).offset(offset).limit(limit)).all()
    return deals

@app.get("/deals/{deal_id}", response_model=Deal)
def read_deal(deal_id: int, session: Session = Depends(get_session)):
    deal = session.get(Deal, deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal

# --- Asset Endpoints ---

@app.post("/assets/", response_model=Asset)
def create_asset(asset: Asset, session: Session = Depends(get_session)):
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset

@app.get("/deals/{deal_id}/assets/", response_model=List[Asset])
def read_deal_assets(deal_id: int, session: Session = Depends(get_session)):
    # Since we removed Foreign Keys, we just query by the integer column
    statement = select(Asset).where(Asset.deal_id == deal_id)
    assets = session.exec(statement).all()
    return assets
