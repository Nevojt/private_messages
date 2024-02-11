from typing import Optional
from pydantic import BaseModel, Field, EmailStr
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
    
    
# class UserCreate(BaseModel):
#     email: EmailStr
#     user_name: str
#     password: str
#     avatar: str
    
        
# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class Token(BaseModel):
#     access_token: str
#     token_type: str

        
        



# class UserOut(BaseModel):
#     id: int
#     user_name: str
#     avatar: str
#     created_at: datetime
    
#     class Config:
#         from_attributes = True