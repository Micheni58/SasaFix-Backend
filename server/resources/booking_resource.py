# routers/booking_router.py - Dev 3

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.models.booking import Booking, BookingStatus as BookingModelStatus
from server.models.serviceprovider import ServiceProvider
from server.models.user import User
from server.schemas.booking_schema import (
    BookingCreate,
    BookingReschedule,
    BookingResponse,
    BookingStatus,
    BookingStatusUpdate,
    BookingUpdate,
)
from server.services import email_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


# ─────────────────────────────────────────────
# VALID STATUS TRANSITIONS
# ─────────────────────────────────────────────

VALID_TRANSITIONS = {
    BookingModelStatus.PENDING: [
        BookingModelStatus.ACCEPTED,
        BookingModelStatus.CANCELLED,
    ],
    BookingModelStatus.ACCEPTED: [
        BookingModelStatus.IN_PROGRESS,
        BookingModelStatus.CANCELLED,
    ],
    BookingModelStatus.IN_PROGRESS: [
        BookingModelStatus.COMPLETED,
        BookingModelStatus.CANCELLED,
    ],
    BookingModelStatus.COMPLETED: [],
    BookingModelStatus.CANCELLED: [],
}


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def _get_booking_or_404(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


def _get_client_or_404(db: Session, client_id: int) -> User:
    client = db.query(User).filter(User.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


def _get_provider_or_404(db: Session, service_provider_id: int) -> ServiceProvider:
    provider = db.query(ServiceProvider).filter(
        ServiceProvider.id == service_provider_id
    ).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Service provider not found")
    return provider


def _validate_schedule(scheduled_start_time, scheduled_end_time) -> None:
    if (
        scheduled_start_time
        and scheduled_end_time
        and scheduled_start_time >= scheduled_end_time
    ):
        raise HTTPException(
            status_code=400,
            detail="scheduled_end_time must be later than scheduled_start_time",
        )


def _validate_status_transition(
    current_status: BookingModelStatus,
    new_status: BookingModelStatus,
) -> None:
    allowed = VALID_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot transition booking from "
                f"'{current_status.value}' to '{new_status.value}'"
            ),
        )


def _booking_email_fields(booking: Booking) -> dict:
    """Extract common booking fields needed for email notifications."""
    return {
        "service_name": booking.service_name,
        "booking_date": str(booking.scheduled_date) if booking.scheduled_date else "N/A",
        "start_time": str(booking.scheduled_start_time) if booking.scheduled_start_time else "N/A",
        "end_time": str(booking.scheduled_end_time) if booking.scheduled_end_time else "N/A",
        "location": booking.location,
        "amount": booking.amount,
        "status": booking.status.value if booking.status else "pending",
    }


# ─────────────────────────────────────────────
# NOTIFICATION HELPERS
# ─────────────────────────────────────────────

def _notify_booking_created(
    booking: Booking, client: User, provider: ServiceProvider
) -> None:
    fields = _booking_email_fields(booking)
    email_service.send_booking_created_email(
        recipient_email=client.email,
        recipient_name=client.full_name,
        other_party_name=provider.name,
        role_label="client",
        **fields,
    )
    email_service.send_booking_created_email(
        recipient_email=provider.contact_email,
        recipient_name=provider.name,
        other_party_name=client.full_name,
        role_label="service provider",
        **fields,
    )


def _notify_booking_confirmed(
    booking: Booking, client: User, provider: ServiceProvider
) -> None:
    fields = _booking_email_fields(booking)
    email_service.send_booking_confirmed_email(
        recipient_email=client.email,
        recipient_name=client.full_name,
        provider_name=provider.name,
        service_name=fields["service_name"],
        booking_date=fields["booking_date"],
        start_time=fields["start_time"],
        end_time=fields["end_time"],
        location=fields["location"],
        amount=fields["amount"],
    )


def _notify_booking_rescheduled(
    booking: Booking, client: User, provider: ServiceProvider
) -> None:
    fields = _booking_email_fields(booking)
    email_service.send_booking_rescheduled_email(
        recipient_email=client.email,
        recipient_name=client.full_name,
        other_party_name=provider.name,
        role_label="client",
        **fields,
    )
    email_service.send_booking_rescheduled_email(
        recipient_email=provider.contact_email,
        recipient_name=provider.name,
        other_party_name=client.full_name,
        role_label="service provider",
        **fields,
    )


def _notify_booking_cancelled(
    booking: Booking, client: User, provider: ServiceProvider
) -> None:
    fields = _booking_email_fields(booking)
    email_service.send_booking_cancelled_email(
        recipient_email=client.email,
        recipient_name=client.full_name,
        other_party_name=provider.name,
        role_label="client",
        **fields,
    )
    email_service.send_booking_cancelled_email(
        recipient_email=provider.contact_email,
        recipient_name=provider.name,
        other_party_name=client.full_name,
        role_label="service provider",
        **fields,
    )


def _notify_job_completed(
    booking: Booking, client: User, provider: ServiceProvider
) -> None:
    email_service.send_job_completed_email(
        client_email=client.email,
        client_name=client.full_name,
        provider_email=provider.contact_email,
        provider_name=provider.name,
        service_name=booking.service_name,
    )


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@router.get("/active", response_model=List[BookingResponse])
def list_active_bookings(db: Session = Depends(get_db)):
    active_statuses = [
        BookingModelStatus.PENDING,
        BookingModelStatus.ACCEPTED,
        BookingModelStatus.IN_PROGRESS,
    ]
    return (
        db.query(Booking)
        .filter(Booking.status.in_(active_statuses))
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/client/{client_id}", response_model=List[BookingResponse])
def list_client_bookings(client_id: int, db: Session = Depends(get_db)):
    _get_client_or_404(db, client_id)
    return (
        db.query(Booking)
        .filter(Booking.client_id == client_id)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/provider/{service_provider_id}", response_model=List[BookingResponse])
def list_provider_bookings(service_provider_id: int, db: Session = Depends(get_db)):
    _get_provider_or_404(db, service_provider_id)
    return (
        db.query(Booking)
        .filter(Booking.service_provider_id == service_provider_id)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/status/{status_value}", response_model=List[BookingResponse])
def list_bookings_by_status(
    status_value: BookingStatus, db: Session = Depends(get_db)
):
    booking_status = BookingModelStatus(status_value.value)
    return (
        db.query(Booking)
        .filter(Booking.status == booking_status)
        .order_by(Booking.created_at.desc())
        .all()
    )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    return _get_booking_or_404(db, booking_id)


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    # Fetch once and reuse — no duplicate queries
    client = _get_client_or_404(db, booking_data.client_id)
    provider = _get_provider_or_404(db, booking_data.service_provider_id)
    _validate_schedule(
        booking_data.scheduled_start_time, booking_data.scheduled_end_time
    )

    booking = Booking(
        client_id=booking_data.client_id,
        service_provider_id=booking_data.service_provider_id,
        service_name=booking_data.service_name,
        description=booking_data.description,
        scheduled_date=booking_data.scheduled_date,
        scheduled_start_time=booking_data.scheduled_start_time,
        scheduled_end_time=booking_data.scheduled_end_time,
        location=booking_data.location,
        latitude=booking_data.latitude,
        longitude=booking_data.longitude,
        amount=booking_data.amount,
        status=BookingModelStatus.PENDING,
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    _notify_booking_created(booking, client, provider)
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int, booking_data: BookingUpdate, db: Session = Depends(get_db)
):
    booking = _get_booking_or_404(db, booking_id)
    update_data = booking_data.model_dump(exclude_unset=True)

    if "client_id" in update_data:
        _get_client_or_404(db, update_data["client_id"])
    if "service_provider_id" in update_data:
        _get_provider_or_404(db, update_data["service_provider_id"])

    start_time = update_data.get("scheduled_start_time", booking.scheduled_start_time)
    end_time = update_data.get("scheduled_end_time", booking.scheduled_end_time)
    _validate_schedule(start_time, end_time)

    if "status" in update_data and update_data["status"] is not None:
        update_data["status"] = BookingModelStatus(update_data["status"].value)

    for field, value in update_data.items():
        setattr(booking, field, value)

    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_data: BookingStatusUpdate,
    db: Session = Depends(get_db),
):
    booking = _get_booking_or_404(db, booking_id)
    new_status = BookingModelStatus(status_data.status.value)

    _validate_status_transition(booking.status, new_status)
    booking.set_status(new_status)
    db.commit()
    db.refresh(booking)

    client = _get_client_or_404(db, booking.client_id)
    provider = _get_provider_or_404(db, booking.service_provider_id)

    if new_status == BookingModelStatus.ACCEPTED:
        _notify_booking_confirmed(booking, client, provider)

    if new_status == BookingModelStatus.COMPLETED:
        _notify_job_completed(booking, client, provider)

    if new_status == BookingModelStatus.CANCELLED:
        _notify_booking_cancelled(booking, client, provider)

    return booking


@router.patch("/{booking_id}/reschedule", response_model=BookingResponse)
def reschedule_booking(
    booking_id: int,
    reschedule_data: BookingReschedule,
    db: Session = Depends(get_db),
):
    booking = _get_booking_or_404(db, booking_id)
    _validate_schedule(
        reschedule_data.scheduled_start_time,
        reschedule_data.scheduled_end_time,
    )

    client = _get_client_or_404(db, booking.client_id)
    provider = _get_provider_or_404(db, booking.service_provider_id)

    booking.scheduled_date = reschedule_data.scheduled_date
    booking.scheduled_start_time = reschedule_data.scheduled_start_time
    booking.scheduled_end_time = reschedule_data.scheduled_end_time

    db.commit()
    db.refresh(booking)

    _notify_booking_rescheduled(booking, client, provider)
    return booking


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = _get_booking_or_404(db, booking_id)

    if not booking.can_be_cancelled():
        raise HTTPException(
            status_code=400, detail="This booking cannot be cancelled"
        )

    client = _get_client_or_404(db, booking.client_id)
    provider = _get_provider_or_404(db, booking.service_provider_id)

    booking.set_status(BookingModelStatus.CANCELLED)
    db.commit()
    db.refresh(booking)

    _notify_booking_cancelled(booking, client, provider)
    return booking