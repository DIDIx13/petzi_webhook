from fastapi import FastAPI, Header, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import hmac
import hashlib
import json
from sqlalchemy.orm import Session
from app import models, schemas, database, utils

app = FastAPI()

# Créer les tables dans la base de données
models.Base.metadata.create_all(bind=database.engine)

# Dépendance pour obtenir une session DB
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/webhook")
async def receive_webhook(
    request: Request, 
    petzi_signature: str = Header(None, alias="Petzi-Signature"),
    db: Session = Depends(get_db)
):
    if not petzi_signature:
        raise HTTPException(status_code=400, detail="Missing Petzi-Signature header")

    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')

    is_valid = utils.verify_signature(body_str, petzi_signature)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Extraire les informations nécessaires
    try:
        details = payload["details"]
        ticket_data = details["ticket"]
        buyer_data = details["buyer"]

        ticket = models.Ticket(
            number=ticket_data["number"],
            type=ticket_data["type"],
            title=ticket_data["title"],
            category=ticket_data["category"],
            event_id=ticket_data["eventId"],
            event=ticket_data["event"],
            cancellation_reason=ticket_data.get("cancellationReason", None),
            generated_at=ticket_data["generatedAt"],
            promoter=ticket_data["promoter"],
            price_amount=float(ticket_data["price"]["amount"]),
            price_currency=ticket_data["price"]["currency"],
            buyer_role=buyer_data["role"],
            buyer_first_name=buyer_data["firstName"],
            buyer_last_name=buyer_data["lastName"],
            buyer_postcode=buyer_data["postcode"]
        )
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid data type: {e}")

    # Persister dans la base de données
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return JSONResponse(status_code=200, content={"message": "Webhook received and processed"})
