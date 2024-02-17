from typing import Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from pydantic import BaseModel
from datetime import datetime



    
        
class SocketModel(BaseModel):
    created_at: datetime
    receiver_id: int
    message: str
    id: int
    user_name: str
    verified: bool
    avatar: str
    is_read: bool
    dir: int
    
    class Config:
        from_attributes = True

class SocketUpdate(BaseModel):
    id: int
    messages: str
    
class SocketDelete(BaseModel):
    id: int

    
class TokenData(BaseModel):
    id: Optional[int] = None
    
class Vote(BaseModel):
    message_id: int
    dir: Annotated[int, Field(strict=True, le=1)]
    
