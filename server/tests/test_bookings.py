# server/tests/test_bookings.py - Dev 3

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.core.database import Base, get_db
from server.main import app
from server.models.user import User
from server.models.serviceprovider import ServiceProvider

# ─────────────────────────────────────────────
# TEST DATABASE SETUP
# Uses the PostgreSQL test database spun up
# by GitHub Actions CI — never touches the
# real Supabase production database
# ─────────────────────────────────────────────

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://testuser:testpassword@localhost:5432/sasafix_test"
)

engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    """
    Replaces the real database session with
    the test database session during tests.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """
    Creates all tables before each test
    and drops them after so every test
    starts with a clean database.
    """
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """
    Provides a database session to tests
    that need to insert data directly.
    """
    database = TestingSessionLocal()
    try:
        yield database
    finally:
        database.close()


client = TestClient(app)


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def create_test_user(db, email="client@test.com"):
    """Creates a user directly in the test database."""
    user = User(
        email=email,
        password="hashedpassword123",
        full_name="Test Client",
        role="client",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_provider(db):
    """
    Creates a service provider directly in the test database.
    NOTE: Once Jeremy updates the ServiceProvider model with
    contact_email, hourly_rate etc, update this function too.
    """
    provider = ServiceProvider(
        name="Test Provider",
        service_type="Plumbing",
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


def create_test_booking(client_id: int, provider_id: int):
    """Creates a booking via the API endpoint."""
    return client.post("/bookings/", json={
        "client_id": client_id,
        "service_provider_id": provider_id,
        "service_name": "Plumbing Repair",
        "description": "Fix leaking kitchen sink",
        "scheduled_date": "2026-06-15",
        "scheduled_start_time": "09:00:00",
        "scheduled_end_time": "11:00:00",
        "location": "Westlands, Nairobi",
        "latitude": -1.2641,
        "longitude": 36.8027,
        "amount": 3000.0
    })


# ─────────────────────────────────────────────
# CREATE BOOKING TESTS
# ─────────────────────────────────────────────

class TestCreateBooking:

    def test_create_booking_success(self, db):
        """Should create a booking and return 201."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        response = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )

        assert response.status_code == 201
        data = response.json()
        assert data["service_name"] == "Plumbing Repair"
        assert data["status"] == "pending"
        assert data["amount"] == 3000.0
        assert data["location"] == "Westlands, Nairobi"

    def test_create_booking_missing_required_fields(self):
        """Should return 422 when required fields are missing."""
        response = client.post("/bookings/", json={})
        assert response.status_code == 422

    def test_create_booking_invalid_client_id(self, db):
        """Should return 404 when client does not exist."""
        provider = create_test_provider(db)
        response = create_test_booking(
            client_id=99999,
            provider_id=provider.id
        )
        assert response.status_code == 404

    def test_create_booking_invalid_provider_id(self, db):
        """Should return 404 when service provider does not exist."""
        user = create_test_user(db)
        response = create_test_booking(
            client_id=user.id,
            provider_id=99999
        )
        assert response.status_code == 404

    def test_create_booking_invalid_schedule(self, db):
        """Should return 400 when end time is before start time."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        response = client.post("/bookings/", json={
            "client_id": user.id,
            "service_provider_id": provider.id,
            "service_name": "Plumbing Repair",
            "scheduled_date": "2026-06-15",
            "scheduled_start_time": "11:00:00",
            "scheduled_end_time": "09:00:00",
            "location": "Westlands, Nairobi",
            "amount": 3000.0
        })

        assert response.status_code == 400

    def test_create_booking_zero_amount(self, db):
        """Should return 422 when amount is zero or negative."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        response = client.post("/bookings/", json={
            "client_id": user.id,
            "service_provider_id": provider.id,
            "service_name": "Plumbing Repair",
            "scheduled_date": "2026-06-15",
            "scheduled_start_time": "09:00:00",
            "scheduled_end_time": "11:00:00",
            "location": "Westlands, Nairobi",
            "amount": 0.0
        })

        assert response.status_code == 422

    def test_new_booking_status_is_pending(self, db):
        """Newly created bookings should always start as pending."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        response = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        assert response.json()["status"] == "pending"


# ─────────────────────────────────────────────
# GET BOOKING TESTS
# ─────────────────────────────────────────────

class TestGetBooking:

    def test_get_booking_success(self, db):
        """Should return a booking by ID."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.get(f"/bookings/{booking_id}")
        assert response.status_code == 200
        assert response.json()["id"] == booking_id

    def test_get_booking_not_found(self):
        """Should return 404 for a booking that does not exist."""
        response = client.get("/bookings/99999")
        assert response.status_code == 404

    def test_get_client_bookings(self, db):
        """Should return all bookings for a specific client."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        create_test_booking(client_id=user.id, provider_id=provider.id)
        create_test_booking(client_id=user.id, provider_id=provider.id)

        response = client.get(f"/bookings/client/{user.id}")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_provider_bookings(self, db):
        """Should return all bookings for a specific service provider."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        create_test_booking(client_id=user.id, provider_id=provider.id)

        response = client.get(f"/bookings/provider/{provider.id}")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_client_bookings_invalid_client(self):
        """Should return 404 when client does not exist."""
        response = client.get("/bookings/client/99999")
        assert response.status_code == 404

    def test_get_active_bookings(self, db):
        """Should return only pending accepted and in_progress bookings."""
        user = create_test_user(db)
        provider = create_test_provider(db)

        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(f"/bookings/{booking_id}/cancel")

        response = client.get("/bookings/active")
        active_ids = [b["id"] for b in response.json()]
        assert booking_id not in active_ids


# ─────────────────────────────────────────────
# STATUS UPDATE TESTS
# ─────────────────────────────────────────────

class TestBookingStatusUpdate:

    def test_update_status_pending_to_accepted(self, db):
        """Provider should be able to accept a pending booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "accepted"

    def test_update_status_accepted_to_in_progress(self, db):
        """Should transition from accepted to in_progress."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        response = client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "in_progress"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "in_progress"

    def test_update_status_in_progress_to_completed(self, db):
        """Should transition from in_progress to completed."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "in_progress"}
        )
        response = client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "completed"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "completed"

    def test_invalid_status_transition_pending_to_completed(self, db):
        """Should not allow skipping from pending directly to completed."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "completed"}
        )
        assert response.status_code == 400

    def test_invalid_status_transition_completed_to_pending(self, db):
        """Should not allow reverting a completed booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "in_progress"}
        )
        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "completed"}
        )
        response = client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "pending"}
        )
        assert response.status_code == 400

    def test_invalid_status_value(self, db):
        """Should return 422 for a completely invalid status string."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        response = client.patch(
            f"/bookings/{booking.json()['id']}/status",
            json={"status": "flying"}
        )
        assert response.status_code == 422


# ─────────────────────────────────────────────
# CANCEL BOOKING TESTS
# ─────────────────────────────────────────────

class TestCancelBooking:

    def test_cancel_pending_booking(self, db):
        """Should successfully cancel a pending booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.patch(f"/bookings/{booking_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cancel_accepted_booking(self, db):
        """Should successfully cancel an accepted booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        response = client.patch(f"/bookings/{booking_id}/cancel")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    def test_cannot_cancel_completed_booking(self, db):
        """Should not allow cancelling a completed booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "accepted"}
        )
        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "in_progress"}
        )
        client.patch(
            f"/bookings/{booking_id}/status",
            json={"status": "completed"}
        )
        response = client.patch(f"/bookings/{booking_id}/cancel")
        assert response.status_code == 400

    def test_cannot_cancel_already_cancelled_booking(self, db):
        """Should not allow cancelling an already cancelled booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        client.patch(f"/bookings/{booking_id}/cancel")
        response = client.patch(f"/bookings/{booking_id}/cancel")
        assert response.status_code == 400

    def test_cancel_nonexistent_booking(self):
        """Should return 404 when trying to cancel a booking that does not exist."""
        response = client.patch("/bookings/99999/cancel")
        assert response.status_code == 404


# ─────────────────────────────────────────────
# RESCHEDULE BOOKING TESTS
# ─────────────────────────────────────────────

class TestRescheduleBooking:

    def test_reschedule_booking_success(self, db):
        """Should successfully reschedule a booking."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.patch(
            f"/bookings/{booking_id}/reschedule",
            json={
                "scheduled_date": "2026-07-20",
                "scheduled_start_time": "14:00:00",
                "scheduled_end_time": "16:00:00"
            }
        )
        assert response.status_code == 200
        assert response.json()["scheduled_date"] == "2026-07-20"

    def test_reschedule_invalid_time(self, db):
        """Should return 400 when rescheduled end time is before start time."""
        user = create_test_user(db)
        provider = create_test_provider(db)
        booking = create_test_booking(
            client_id=user.id,
            provider_id=provider.id
        )
        booking_id = booking.json()["id"]

        response = client.patch(
            f"/bookings/{booking_id}/reschedule",
            json={
                "scheduled_date": "2026-07-20",
                "scheduled_start_time": "16:00:00",
                "scheduled_end_time": "14:00:00"
            }
        )
        assert response.status_code == 400

    def test_reschedule_nonexistent_booking(self):
        """Should return 404 when trying to reschedule a booking that does not exist."""
        response = client.patch(
            "/bookings/99999/reschedule",
            json={
                "scheduled_date": "2026-07-20",
                "scheduled_start_time": "09:00:00",
                "scheduled_end_time": "11:00:00"
            }
        )
        assert response.status_code == 404