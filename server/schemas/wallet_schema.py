# schemas/wallet_schema.py - Stercy

from pydantic import BaseModel, Field

class walletCreate(BaseModel):
    user_id: int
    balance: float