# app/notifications/email.py

from flask import render_template, current_app
from flask_mail import Message
from app.extensions import mail


import threading

def send_async_mail(app, msg):
    with app.app_context():
        from app.extensions import mail
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Async mail error: {e}")

def _send(subject, recipients, template, **kwargs):
    try:
        msg = Message(
            subject    = subject,
            recipients = [recipients] if isinstance(recipients, str) else recipients,
            html       = render_template(template, **kwargs)
        )
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Mail send error: {e}")

def send_match_notification(recipient_email, recipient_name,
                             my_item, other_item, score, view_url):
    """Notify a user that their item has a high-confidence match."""
    _send(
        subject       = f"Campus Lost & Found — {score}% Match Found!",
        recipients    = recipient_email,
        template      = "emails/match_found.html",
        recipient_name = recipient_name,
        my_item       = my_item,
        other_item    = other_item,
        score         = score,
        view_url      = view_url,
    )


def send_claim_submitted(finder_email, finder_name,
                          claimer_name, item_name, incoming_url):
    """Notify finder that someone claimed their item."""
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
    """Notify claimant their claim was approved."""
    _send(
        subject      = f"Campus Lost & Found — Your Claim Was Approved!",
        recipients   = claimer_email,
        template     = "emails/claim_approved.html",
        claimer_name = claimer_name,
        item_name    = item_name,
        finder_name  = finder_name,
        finder_email = finder_email,
    )


def send_claim_rejected(claimer_email, claimer_name, item_name):
    """Notify claimant their claim was rejected."""
    _send(
        subject      = "Campus Lost & Found — Claim Update",
        recipients   = claimer_email,
        template     = "emails/claim_rejected.html",
        claimer_name = claimer_name,
        item_name    = item_name,
    )