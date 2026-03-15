# models/payoutrequest.py - Stercy
#  id, conversation_id (foreign key to Conversation),
#  sender_id (foreign key to User), content, is_read, created_at
from sqlalchemy import Column, Integer, String, ForeignKey
from server.core.database import Base

class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True, index=True)
    # user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Integer)
    