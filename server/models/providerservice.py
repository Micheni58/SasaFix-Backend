# models/providerservice.py - Jeremy
#  id, provider_id (foreign key to ServiceProvider), 
# service_name (e.g. Pipe Installation, Leak Repair), description, created_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class ProviderService(Base):
    __tablename__ = "provider_services"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String)
    description = Column(String)

    def __repr__(self):
        return f"<ProviderService(id={self.id}, service_name='{self.service_name}', description='{self.description}')>"