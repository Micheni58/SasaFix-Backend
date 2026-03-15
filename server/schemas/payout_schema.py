# schemas/payout_schema.py - Stercy

from pydantic import BaseModel, Field
class ServiceProviderCreate(BaseModel):
    name: str
    description: str
    contact_email: str
    service_type: str
    years_of_experience: int
    hourly_rate: float