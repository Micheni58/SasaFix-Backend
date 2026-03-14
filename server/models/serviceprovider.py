# models/serviceprovider.py - Jeremy
# id, user_id (foreign key to User), 
# bio, service_category, years_of_experience, 
# hourly_rate, is_verified, verification_status (pending, verified, rejected), 
# verification_rejection_reason, 
# smile_identity_job_id, 
# national_id_front_url, 
# national_id_back_url, 
# selfie_url, is_premium, average_rating, total_reviews, 
# total_jobs_completed, response_time_minutes, 
# member_since, created_at, updated_at
from sqlalchemy import Column, Integer, String
from server.core.database import Base

class ServiceProvider(Base):
    __tablename__ = "service_providers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    service_type = Column(String)

    def __repr__(self):
        return f"<ServiceProvider(id={self.id}, name='{self.name}', service_type='{self.service_type}')>"