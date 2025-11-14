"""Data models for the alerting service."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class IndexData(BaseModel):
    """Model for index price data."""
    symbol: str
    date: datetime
    close: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None


class Alert(BaseModel):
    """Model for alert."""
    index_name: str
    symbol: str
    current_price: float
    reference_price: float
    reference_date: datetime
    percentage_change: float
    message: str
    timestamp: datetime
    trigger_type: str
    threshold: Optional[float] = None  # Threshold that triggered this alert
