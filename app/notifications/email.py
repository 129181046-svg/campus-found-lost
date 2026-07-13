# app/notifications/email.py

import requests
from flask import render_template, current_app

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send(subject, recipients, template, **kwargs):
    recipients = [recipients] if isinstance(recipients, str) else recipients

    payload = {
        "sender": {
            "name": "Campus Lost & Found",
            "email": current_app.config["MAIL_USERNAME"],  # must match your verified Brevo sender
        },
        "to": [{"email": r} for r in recipients],
        "subject": subject,
        "htmlContent": render_template(template, **kwargs),
    }

    headers = {
        "accept": "application/json",
        "api-key": current_app.config["BREVO_API_KEY"],
        "content-type": "application/json",
    }

    try:
        resp = requests.post(BREVO_API_URL, json=payload, headers=headers, timeout=10)
        if resp.status_code >= 400:
            current_app.logger.error(f"Brevo send failed: {resp.status_code} {resp.text}")
    except Exception as e:
        current_app.logger.error(f"Mail send error: {e}")


def send_match_notification(recipient_email, recipient_name,
                             my_item, other_item, score, view_url):
    _send(
        subject        = f"Campus Lost & Found — {score}% Match Found!",
        recipients     = recipient_email,
        template       = "emails/match_found.html",
        recipient_name = recipient_name,
        my_item        = my_item,
        other_item     = other_item,
        score          = score,
        view_url       = view_url,
    )


def send_claim_submitted(finder_email, finder_name,
                          claimer_name, item_name, incoming_url):
    _send(
        subject      = f"Campus Lost & Found — New Claim on '{item_name}'",
        recipients   = finder_email,
        template     = "emails/claim_submitted.html",
        finder_name  = finder_name,
        claimer_name = claimer_name,
        item_name    = item_name,
        incoming_url = incoming_url,
    )


def send_claim_approved(claimer_email, claimer_name,
                         item_name, finder_name, finder_email):
    _send(
        subject      = "Campus Lost & Found — Your Claim Was Approved!",
        recipients   = claimer_email,
        template     = "emails/claim_approved.html",
        claimer_name = claimer_name,
        item_name    = item_name,
        finder_name  = finder_name,
        finder_email = finder_email,
    )


def send_claim_rejected(claimer_email, claimer_name, item_name):
    _send(
        subject      = "Campus Lost & Found — Claim Update",
        recipients   = claimer_email,
        template     = "emails/claim_rejected.html",
        claimer_name = claimer_name,
        item_name    = item_name,
    )