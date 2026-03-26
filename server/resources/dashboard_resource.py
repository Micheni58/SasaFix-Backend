from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.security import ALGORITHM, SECRET_KEY
from server.models.booking import Booking
from server.models.user import User
from server.models.wallet import Wallet

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
    )

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError as exc:
        raise unauthorized from exc

    if not user_id:
        raise unauthorized

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise unauthorized

    return user


@router.get("/client")
def get_client_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This dashboard is only available for client users",
        )

    active_statuses = ["pending", "accepted", "in_progress"]

    active_jobs = (
        db.query(Booking)
        .filter(Booking.client_id == current_user.id, Booking.status.in_(active_statuses))
        .order_by(Booking.created_at.desc())
        .all()
    )
    completed_jobs = (
        db.query(Booking)
        .filter(Booking.client_id == current_user.id, Booking.status == "completed")
        .order_by(Booking.updated_at.desc())
        .all()
    )
    recent_bookings = (
        db.query(Booking)
        .filter(Booking.client_id == current_user.id)
        .order_by(Booking.created_at.desc())
        .limit(5)
        .all()
    )
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()

    loyalty_target = 10
    loyalty_points = len(completed_jobs)

    return {
        "user_info": {
            "id": current_user.id,
            "name": current_user.full_name,
            "location": current_user.location,
            "profile_pic": current_user.profile_photo_url,
        },
        "active_jobs_count": len(active_jobs),
        "active_booking": [
            {
                "id": booking.id,
                "service": booking.service_name,
                "date": booking.scheduled_date,
                "status": booking.status,
                "amount": booking.amount,
            }
            for booking in active_jobs
        ],
        "completed_jobs_count": len(completed_jobs),
        "wallet": {
            "balance": wallet.balance if wallet else 0.0,
            "currency": wallet.currency if wallet else "KES",
        },
        "loyalty_progress": {
            "completed_jobs": loyalty_points,
            "next_reward_at": loyalty_target,
            "progress_percent": min((loyalty_points / loyalty_target) * 100, 100),
        },
        "recent_bookings": [
            {
                "id": booking.id,
                "service": booking.service_name,
                "worker": booking.provider_id,
                "date": booking.scheduled_date,
                "status": booking.status,
                "amount": booking.amount,
            }
            for booking in recent_bookings
        ],
    }
