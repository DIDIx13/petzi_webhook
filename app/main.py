from fastapi import FastAPI, Header, HTTPException, Request, Depends, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import hmac
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas, database, utils
from typing import Optional, List
from datetime import datetime

app = FastAPI()

# Configuration des templates
templates = Jinja2Templates(directory="app/templates")

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
        # Enregistrer la requête avec un statut 400
        body_bytes = await request.body()
        body_str = body_bytes.decode('utf-8')
        webhook_request = models.WebhookRequest(
            payload=body_str,
            http_status=400,
            error_message="Missing Petzi-Signature header"
        )
        db.add(webhook_request)
        db.commit()
        db.refresh(webhook_request)
        raise HTTPException(status_code=400, detail="Missing Petzi-Signature header")

    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')

    is_valid = utils.verify_signature(body_str, petzi_signature)

    if not is_valid:
        # Enregistrer la requête avec un statut 400
        webhook_request = models.WebhookRequest(
            payload=body_str,
            http_status=400,
            error_message="Invalid signature"
        )
        db.add(webhook_request)
        db.commit()
        db.refresh(webhook_request)
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        # Enregistrer la requête avec un statut 400
        webhook_request = models.WebhookRequest(
            payload=body_str,
            http_status=400,
            error_message="Invalid JSON payload"
        )
        db.add(webhook_request)
        db.commit()
        db.refresh(webhook_request)
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
        # Enregistrer la requête avec un statut 400
        webhook_request = models.WebhookRequest(
            payload=body_str,
            http_status=400,
            error_message=f"Missing field: {e}"
        )
        db.add(webhook_request)
        db.commit()
        db.refresh(webhook_request)
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except ValueError as e:
        # Enregistrer la requête avec un statut 400
        webhook_request = models.WebhookRequest(
            payload=body_str,
            http_status=400,
            error_message=f"Invalid data type: {e}"
        )
        db.add(webhook_request)
        db.commit()
        db.refresh(webhook_request)
        raise HTTPException(status_code=400, detail=f"Invalid data type: {e}")

    # Persister dans la base de données
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Extraire les champs spécifiques pour WebhookRequest
    try:
        buyer_first_name = buyer_data["firstName"]
        buyer_last_name = buyer_data["lastName"]
        event_name = ticket_data["event"]
        price_amount = float(ticket_data["price"]["amount"])
    except KeyError:
        buyer_first_name = buyer_last_name = event_name = price_amount = None

    # Enregistrer la requête avec un statut 200 et les champs spécifiques
    webhook_request = models.WebhookRequest(
        payload=body_str,
        http_status=200,
        error_message=None,
        buyer_first_name=buyer_first_name,
        buyer_last_name=buyer_last_name,
        event_name=event_name,
        price_amount=price_amount
    )
    db.add(webhook_request)
    db.commit()

    return JSONResponse(status_code=200, content={"message": "Webhook received and processed"})

@app.get("/history", response_class=HTMLResponse)
def get_history(
    request: Request,
    page: int = 1,
    http_status: Optional[int] = Query(None, description="Filtrer par statut HTTP"),
    start_date: Optional[str] = Query(None, description="Date de début au format YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="Date de fin au format YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    per_page = 20

    query = db.query(models.WebhookRequest)

    # Appliquer les filtres si fournis
    if http_status:
        query = query.filter(models.WebhookRequest.http_status == http_status)
    if start_date:
        try:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(models.WebhookRequest.timestamp >= start_datetime)
        except ValueError:
            pass  # Ignorer le filtre si la date est invalide
    if end_date:
        try:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(models.WebhookRequest.timestamp <= end_datetime)
        except ValueError:
            pass  # Ignorer le filtre si la date est invalide

    total = query.count()
    total_pages = (total + per_page - 1) // per_page

    webhook_requests = query.order_by(models.WebhookRequest.timestamp.desc())\
        .offset((page - 1) * per_page)\
        .limit(per_page)\
        .all()

    # Recueillir les données pour le graphique
    sales_data = db.query(
        func.date_trunc('day', models.WebhookRequest.timestamp).label('day'),
        func.count(models.WebhookRequest.id).label('ticket_count')
    ).filter(models.WebhookRequest.http_status == 200)\
    .group_by('day').order_by('day').all()

    days = [day.strftime('%Y-%m-%d') for day, count in sales_data]
    counts = [count for day, count in sales_data]

    return templates.TemplateResponse("history.html", {
        "request": request, 
        "requests": webhook_requests,
        "page": page,
        "total_pages": total_pages,
        "http_status": http_status,
        "start_date": start_date if start_date else "",
        "end_date": end_date if end_date else "",
        "days": days,
        "counts": counts
    })

@app.get("/history/{request_id}", response_class=HTMLResponse)
def get_request_detail(request: Request, request_id: int, db: Session = Depends(get_db)):
    webhook_request = db.query(models.WebhookRequest).filter(models.WebhookRequest.id == request_id).first()
    if not webhook_request:
        raise HTTPException(status_code=404, detail="Requête webhook non trouvée")
    
    try:
        payload = json.loads(webhook_request.payload)
    except json.JSONDecodeError:
        payload = {"error": "Payload non valide"}

    return templates.TemplateResponse("detail.html", {
        "request": request,
        "webhook_request": webhook_request,
        "payload": payload
    })
