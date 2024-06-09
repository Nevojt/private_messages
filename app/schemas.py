from typing import Optional
from pydantic import BaseModel, Field
from typing import Annotated
from pydantic import BaseModel
from datetime import datetime



    
        
class SocketModel(BaseModel):
    id: int
    created_at: datetime
    receiver_id: int
    message: Optional[str] = None
    fileUrl: Optional[str] = None
    id_return: Optional[int] = None
    user_name: str
    verified: bool
    avatar: str
    is_read: bool
    vote: int
    edited: bool
    
    class Config:
        from_attributes = True

class SocketUpdate(BaseModel):
    id: int
    message: str
    
class SocketDelete(BaseModel):
    id: int

    
class TokenData(BaseModel):
    id: Optional[int] = None
    
class Vote(BaseModel):
    message_id: int
    dir: Annotated[int, Field(strict=True, le=1)]
    
