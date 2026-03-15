# models/conversation.py - Stercy
# id, client_id (foreign key to User), 
# provider_id (foreign key to ServiceProvider), 
# booking_id (nullable foreign key to Booking), last_message_at, created_at
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from server.core.database import Base   

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    
    last_message = Column(String)
    last_message_time = Column(DateTime)

   