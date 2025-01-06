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
    details: dict  # Nous allons extraire les détails manuellement dans main.py
