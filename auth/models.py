from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime

class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
