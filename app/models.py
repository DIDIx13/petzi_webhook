from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    event_id = Column(Integer, nullable=False)
    event = Column(String(100), nullable=False)
    cancellation_reason = Column(String(200), nullable=True)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    promoter = Column(String(100), nullable=False)
    price_amount = Column(Float, nullable=False)
    price_currency = Column(String(10), nullable=False)
    buyer_role = Column(String(50), nullable=False)
    buyer_first_name = Column(String(50), nullable=False)
    buyer_last_name = Column(String(50), nullable=False)
    buyer_postcode = Column(String(20), nullable=False)

    def __repr__(self):
        return f'<Ticket {self.number}>'

class WebhookRequest(Base):
    __tablename__ = "webhook_requests"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    payload = Column(Text, nullable=False)
    http_status = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)

    def __repr__(self):
        return f'<WebhookRequest {self.id} - Status {self.http_status}>'
