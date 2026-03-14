# review_schema.py - Caleb

from pydantic import BaseModel, Field

class ServiceProviderCreate(BaseModel):
    name: str
    description: str
    contact_email: str          