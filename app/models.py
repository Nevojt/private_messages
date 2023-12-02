from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class PrivateMessage(Base):
    __tablename__ = 'private_messages'
    
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True)
    messages = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    is_read = Column(Boolean, nullable=False, default=True)
    
    


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False, index=True, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=False, server_default='https://tygjaceleczftbswxxei.supabase.co/storage/v1/object/public/image_bucket/content%20common%20chat/Avatar%20Desktop/avatar_default.jpg')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    