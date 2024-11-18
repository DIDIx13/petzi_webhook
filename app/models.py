from . import db
from datetime import datetime

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, nullable=False)
    event = db.Column(db.String(100), nullable=False)
    cancellation_reason = db.Column(db.String(200), nullable=True)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    promoter = db.Column(db.String(100), nullable=False)
    price_amount = db.Column(db.Float, nullable=False)
    price_currency = db.Column(db.String(10), nullable=False)
    buyer_role = db.Column(db.String(50), nullable=False)
    buyer_first_name = db.Column(db.String(50), nullable=False)
    buyer_last_name = db.Column(db.String(50), nullable=False)
    buyer_postcode = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Ticket {self.number}>'
