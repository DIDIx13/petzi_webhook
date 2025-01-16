from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Location(BaseModel):
    name: str
    street: str
    city: str
    postcode: str

class Session(BaseModel):
    name: str
    date: str
    time: str
    doors: str
    location: Location

class Price(BaseModel):
    amount: float
    currency: str

class TicketDetails(BaseModel):
    number: str
    type: str
    title: str
    category: str
    eventId: int
    event: str
    cancellationReason: Optional[str] = None
    generatedAt: datetime
    sessions: List[Session]
    promoter: str
    price: Price

class Buyer(BaseModel):
    role: str
    firstName: str
    lastName: str
    postcode: str

class WebhookPayload(BaseModel):
    event: str
    details: dict  # Extraction manuelle dans main.py

class WebhookRequestDisplay(BaseModel):
    id: int
    timestamp: datetime
    http_status: int
    error_message: Optional[str] = None
    buyer_first_name: Optional[str] = None
    buyer_last_name: Optional[str] = None
    event_name: Optional[str] = None
    price_amount: Optional[float] = None

    class Config:
        from_attributes = True

class WebhookRequestDetail(BaseModel):
    id: int
    timestamp: datetime
    http_status: int
    error_message: Optional[str] = None
    payload: dict

    class Config:
        from_attributes = True
