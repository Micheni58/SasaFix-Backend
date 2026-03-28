# services/email_service.py - Dev 3
# Description: Outbound booking emails for Sasafix using SendGrid
# Covers: booking created, confirmed, rescheduled, cancelled, job completed

import os

from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL", "noreply@sasafix.co.ke")
FROM_NAME = os.getenv("SENDGRID_FROM_NAME", "Sasafix")
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")


def _safe_name(value: str | None) -> str:
    """Returns the name or a fallback greeting if name is missing."""
    return value or "there"


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Core SendGrid email sender.
    All booking email functions call this internally.
    """
    if not to_email or not SENDGRID_API_KEY:
        print("SendGrid not configured or recipient email missing.")
        return False
    message = Mail(
        from_email=(FROM_EMAIL, FROM_NAME),
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in (200, 202)
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False


def _base_email_template(
    title: str, body_content: str, cta_link: str, cta_label: str
) -> str:
    """
    Shared HTML wrapper used by all booking emails.
    Keeps branding consistent across all emails —
    blue header, white body, CTA button, footer.
    """
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background:#1D4ED8; padding:20px; border-radius:8px 8px 0 0;">
            <h1 style="color:#fff; margin:0; font-size:22px;">Sasafix</h1>
            <p style="color:#BFDBFE; margin:4px 0 0 0; font-size:13px;">
                Local Services Marketplace
            </p>
        </div>
        <div style="background:#fff; padding:24px; border:1px solid #E5E7EB;
                    border-top:none; border-radius:0 0 8px 8px;">
            <h2 style="color:#1D4ED8;">{title}</h2>
            {body_content}
            <p style="margin:24px 0;">
                <a href="{cta_link}"
                   style="background:#1D4ED8;color:#fff;padding:12px 20px;
                   text-decoration:none;border-radius:6px;font-size:15px;">
                   {cta_label}
                </a>
            </p>
            <p style="color:#9CA3AF; font-size:12px; margin-top:24px;">
                — The Sasafix Team
            </p>
        </div>
    </div>
    """


def _booking_details_block(
    service_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    location: str,
    amount: float,
    status: str,
) -> str:
    """
    Reusable HTML block showing booking details.
    Used inside booking created, rescheduled and cancelled emails.
    """
    return f"""
    <div style="background:#F3F4F6; padding:16px; border-radius:8px; margin:16px 0;">
        <p style="margin:4px 0;"><strong>Service:</strong> {service_name}</p>
        <p style="margin:4px 0;"><strong>Date:</strong> {booking_date}</p>
        <p style="margin:4px 0;"><strong>Time:</strong> {start_time} - {end_time}</p>
        <p style="margin:4px 0;"><strong>Location:</strong> {location}</p>
        <p style="margin:4px 0;"><strong>Amount:</strong> KES {amount:,.2f}</p>
        <p style="margin:4px 0;"><strong>Status:</strong> {status.capitalize()}</p>
    </div>
    """


# ─────────────────────────────────────────────
# BOOKING EMAILS
# ─────────────────────────────────────────────

def send_booking_created_email(
    recipient_email: str,
    recipient_name: str,
    other_party_name: str,
    service_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    location: str,
    amount: float,
    status: str,
    role_label: str,
) -> bool:
    """
    Sent to BOTH client and provider when a booking is created.
    role_label tells the recipient whether they are the client
    or the service provider in this booking.
    Called in: booking_router.py -> create_booking()
    """
    body = f"""
    <p>Hi <strong>{_safe_name(recipient_name)}</strong>,</p>
    <p>A new booking has been created.
       You are receiving this as the <strong>{role_label}</strong>.</p>
    <p>Other party: <strong>{other_party_name}</strong></p>
    {_booking_details_block(
        service_name, booking_date, start_time,
        end_time, location, amount, status
    )}
    """
    html = _base_email_template(
        title="Booking Created",
        body_content=body,
        cta_link=f"{BASE_URL}/bookings",
        cta_label="View Booking",
    )
    return send_email(recipient_email, "Sasafix — New Booking Created", html)


def send_booking_confirmed_email(
    recipient_email: str,
    recipient_name: str,
    provider_name: str,
    service_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    location: str,
    amount: float,
) -> bool:
    """
    Sent to the CLIENT only when the provider accepts the booking.
    Called in: booking_router.py -> update_booking_status()
    when new_status == ACCEPTED
    """
    body = f"""
    <p>Hi <strong>{_safe_name(recipient_name)}</strong>,</p>
    <p>Great news! <strong>{provider_name}</strong> has accepted
       your booking for <strong>{service_name}</strong>.</p>
    {_booking_details_block(
        service_name, booking_date, start_time,
        end_time, location, amount, "accepted"
    )}
    """
    html = _base_email_template(
        title="Booking Confirmed!",
        body_content=body,
        cta_link=f"{BASE_URL}/bookings",
        cta_label="View Booking",
    )
    return send_email(recipient_email, "Sasafix — Booking Confirmed", html)


def send_booking_rescheduled_email(
    recipient_email: str,
    recipient_name: str,
    other_party_name: str,
    service_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    location: str,
    amount: float,
    status: str,
    role_label: str,
) -> bool:
    """
    Sent to BOTH client and provider when a booking is rescheduled.
    Called in: booking_router.py -> reschedule_booking()
    """
    body = f"""
    <p>Hi <strong>{_safe_name(recipient_name)}</strong>,</p>
    <p>Your booking as the <strong>{role_label}</strong> has been rescheduled.
       Here are the updated details:</p>
    <p>Other party: <strong>{other_party_name}</strong></p>
    {_booking_details_block(
        service_name, booking_date, start_time,
        end_time, location, amount, status
    )}
    <p>Please review the updated schedule and plan accordingly.</p>
    """
    html = _base_email_template(
        title="Booking Rescheduled",
        body_content=body,
        cta_link=f"{BASE_URL}/bookings",
        cta_label="View Booking",
    )
    return send_email(recipient_email, "Sasafix — Booking Rescheduled", html)


def send_booking_cancelled_email(
    recipient_email: str,
    recipient_name: str,
    other_party_name: str,
    service_name: str,
    booking_date: str,
    start_time: str,
    end_time: str,
    location: str,
    amount: float,
    status: str,
    role_label: str,
) -> bool:
    """
    Sent to BOTH client and provider when a booking is cancelled.
    Called in: booking_router.py -> cancel_booking()
    and update_booking_status() when new_status == CANCELLED
    """
    body = f"""
    <p>Hi <strong>{_safe_name(recipient_name)}</strong>,</p>
    <p>Your booking as the <strong>{role_label}</strong> has been cancelled.</p>
    <p>Other party: <strong>{other_party_name}</strong></p>
    {_booking_details_block(
        service_name, booking_date, start_time,
        end_time, location, amount, status
    )}
    <p>If this was unexpected, please contact our support team.</p>
    """
    html = _base_email_template(
        title="Booking Cancelled",
        body_content=body,
        cta_link=f"{BASE_URL}/bookings",
        cta_label="View Bookings",
    )
    return send_email(recipient_email, "Sasafix — Booking Cancelled", html)


def send_job_completed_email(
    client_email: str,
    client_name: str,
    provider_email: str,
    provider_name: str,
    service_name: str,
) -> bool:
    """
    Sent to BOTH client and provider when a job is marked completed.
    Client is prompted to leave a review.
    Provider is directed to check their earnings.
    Called in: booking_router.py -> update_booking_status()
    when new_status == COMPLETED
    """
    client_body = f"""
    <p>Hi <strong>{_safe_name(client_name)}</strong>,</p>
    <p>Your job for <strong>{service_name}</strong>
       has been marked as completed.</p>
    <p>We hope you had a great experience!
       Please take a moment to leave a review.</p>
    """
    client_html = _base_email_template(
        title="Job Completed!",
        body_content=client_body,
        cta_link=f"{BASE_URL}/bookings",
        cta_label="Leave a Review",
    )
    send_email(client_email, "Sasafix — Job Completed", client_html)

    provider_body = f"""
    <p>Hi <strong>{_safe_name(provider_name)}</strong>,</p>
    <p>The job for <strong>{service_name}</strong>
       has been marked as completed.</p>
    <p>Your earnings have been updated.
       Check your dashboard for the latest balance.</p>
    """
    provider_html = _base_email_template(
        title="Job Completed!",
        body_content=provider_body,
        cta_link=f"{BASE_URL}/provider/earnings",
        cta_label="View Earnings",
    )
    send_email(provider_email, "Sasafix — Job Completed", provider_html)

    return True
