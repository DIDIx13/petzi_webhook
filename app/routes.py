from flask import Blueprint, render_template, request, flash, redirect, url_for
from .petzi_simulator import simulate_webhook
from .models import Ticket
from . import db
import hmac
import hashlib
import json
import os

main = Blueprint('main', __name__)

def verify_signature(request, secret):
    signature = request.headers.get('Petzi-Signature')
    if not signature:
        return False

    try:
        sig_timestamp, sig_digest = signature.split(',v1=')
        sig_timestamp = sig_timestamp.split('=')[1]
    except (ValueError, IndexError):
        return False

    body = request.get_data(as_text=True)
    body_to_sign = f'{sig_timestamp}.{body}'.encode()
    expected_digest = hmac.new(secret.encode(), body_to_sign, hashlib.sha256).hexdigest()

    return hmac.compare_digest(expected_digest, sig_digest)

@main.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        secret = request.form.get('secret') or os.getenv('PETZI_SECRET', 'AEeyJhbGciOiJIUzUxMiIsImlzcyI6')

        if not url:
            flash('Webhook URL is required!', 'danger')
            return redirect(url_for('main.index'))

        try:
            # Simulate sending the webhook
            simulate_webhook(url, secret)
            flash('Webhook sent successfully!', 'success')
        except Exception as e:
            flash(f'An error occurred: {e}', 'danger')

        return redirect(url_for('main.index'))

    return render_template('index.html')

@main.route('/webhook', methods=['POST'])
def webhook():
    secret = os.getenv('PETZI_SECRET', 'AEeyJhbGciOiJIUzUxMiIsImlzcyI6')

    if not verify_signature(request, secret):
        return {'message': 'Invalid signature'}, 400

    data = request.get_json()
    if not data:
        return {'message': 'No JSON payload received'}, 400

    try:
        # Extract data and create a Ticket instance
        ticket_data = data.get('details', {}).get('ticket', {})
        buyer_data = data.get('details', {}).get('buyer', {})

        ticket = Ticket(
            number=ticket_data.get('number'),
            type=ticket_data.get('type'),
            title=ticket_data.get('title'),
            category=ticket_data.get('category'),
            event_id=ticket_data.get('eventId'),
            event=ticket_data.get('event'),
            cancellation_reason=ticket_data.get('cancellationReason'),
            generated_at=datetime.fromisoformat(ticket_data.get('generatedAt').replace('Z', '+00:00')),
            promoter=ticket_data.get('promoter'),
            price_amount=float(ticket_data.get('price', {}).get('amount')),
            price_currency=ticket_data.get('price', {}).get('currency'),
            buyer_role=buyer_data.get('role'),
            buyer_first_name=buyer_data.get('firstName'),
            buyer_last_name=buyer_data.get('lastName'),
            buyer_postcode=buyer_data.get('postcode')
        )

        db.session.add(ticket)
        db.session.commit()

        return {'message': 'Webhook received and data persisted.'}, 200

    except Exception as e:
        return {'message': f'Error processing webhook: {e}'}, 500
