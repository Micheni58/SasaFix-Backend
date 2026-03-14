# models/user.py - Jeremy
# id, first_name, 
# last_name, email, phone_number, password_hash, 
# role (client or service_provider or admin), 
# profile_photo_url, location, created_at, updated_at, 
# is_active, is_suspended
from sqlalchemy import Column, Integer, String
from server.core.database import Base  

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    