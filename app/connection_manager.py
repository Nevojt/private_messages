from datetime import datetime
import json
import pytz
import logging
from fastapi import WebSocket
from app.database import async_session_maker
from app import models
from sqlalchemy import insert
from typing import Dict, Optional, Tuple


# Налаштування логування
logging.basicConfig(filename='_log/connect_manager.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)




       # Connecting Private Messages     
class ConnectionManagerPrivate:
    def __init__(self):
        self.active_connections: Dict[Tuple[int, int], WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int, recipient_id: int):
        await websocket.accept()
        self.active_connections[(user_id, recipient_id)] = websocket

    async def disconnect(self, user_id: int, recipient_id: int):
        self.active_connections.pop((user_id, recipient_id), None)

    async def send_private_message(self, message: str, sender_id: int, recipient_id: int,
                                   user_name: str, verified: bool,
                                   avatar: str, is_read: bool):
        
        sender_to_recipient = (sender_id, recipient_id)
        recipient_to_sender = (recipient_id, sender_id)
        
        timezone = pytz.timezone('UTC')
        current_time_utc = datetime.now(timezone).isoformat()
        message_id = None
        vote_count = 0
        
        message_id = await self.add_private_message_to_database(message, sender_id, recipient_id)
        
        message_data = {
            "created_at": current_time_utc,
            "sender_id": sender_id,
            "id": message_id,
            "messages": message,
            "imageUrl": None,
            "user_name": user_name,
            "verified": verified,
            "avatar": avatar,
            "is_read": is_read,
            "vote": vote_count
        }
        
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        if sender_to_recipient in self.active_connections:
            await self.active_connections[sender_to_recipient].send_text(message_json)

        if recipient_to_sender in self.active_connections:
            await self.active_connections[recipient_to_sender].send_text(message_json)
        
    

    @staticmethod
    async def add_private_message_to_database(message: str, sender_id: int, recipient_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.PrivateMessage).values(messages=message, sender_id=sender_id, recipient_id=recipient_id)
            result = await session.execute(stmt)
            await session.commit()
            
            message_id = result.inserted_primary_key[0]
            return message_id

            
    async def send_private_file(self, fileUrl: str, sender_id: int, recipient_id: int,
                                   user_name: str, verified: bool,
                                   avatar: str, is_read: bool):
        
        sender_to_recipient = (sender_id, recipient_id)
        recipient_to_sender = (recipient_id, sender_id)
        
        timezone = pytz.timezone('UTC')
        current_time_utc = datetime.now(timezone).isoformat()
        message_id = None
        vote_count = 0
        
        message_id = await self.add_private_file_to_database(fileUrl, sender_id, recipient_id)
        
        message_data = {
            "created_at": current_time_utc,
            "sender_id": sender_id,
            "id": message_id,
            "messages": None,
            "fileUrl": fileUrl,
            "user_name": user_name,
            "verified": verified,
            "avatar": avatar,
            "is_read": is_read,
            "vote": vote_count
        }
        
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        if sender_to_recipient in self.active_connections:
            await self.active_connections[sender_to_recipient].send_text(message_json)

        if recipient_to_sender in self.active_connections:
            await self.active_connections[recipient_to_sender].send_text(message_json)
        
    

    @staticmethod
    async def add_private_file_to_database(fileUrl: str, sender_id: int, recipient_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.PrivateMessage).values(fileUrl=fileUrl, sender_id=sender_id, recipient_id=recipient_id)
            result = await session.execute(stmt)
            await session.commit()
            
            message_id = result.inserted_primary_key[0]
            return message_id
        
        
    async def send_private_all(self, message: Optional[str], file: Optional[str],
                               sender_id: int, recipient_id: int,
                               user_name: str, verified: bool,
                               avatar: str, id_return: Optional[int],
                               is_read: bool):
        
        sender_to_recipient = (sender_id, recipient_id)
        recipient_to_sender = (recipient_id, sender_id)
        
        timezone = pytz.timezone('UTC')
        current_time_utc = datetime.now(timezone).isoformat()
        message_id = None
        vote_count = 0
        
        message_id = await self.add_private_all_to_database(sender_id, recipient_id, message, file, id_return, is_read)
        
        message_data = {
            "created_at": current_time_utc,
            "sender_id": sender_id,
            "id": message_id,
            "messages": message if message is not None else None,
            "fileUrl": file if file is not None else None,
            "user_name": user_name,
            "verified": verified,
            "avatar": avatar,
            "is_read": is_read,
            "vote": vote_count,
            "id_return": id_return if id_return is not None else None,
            "edited": False
        }
        
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        if sender_to_recipient in self.active_connections:
            await self.active_connections[sender_to_recipient].send_text(message_json)

        if recipient_to_sender in self.active_connections:
            await self.active_connections[recipient_to_sender].send_text(message_json)
        
    

    @staticmethod
    async def add_private_all_to_database(sender_id: int, recipient_id: int,
                                          messages: Optional[str], file: Optional[str],
                                          id_return: Optional[int], is_read: bool):
        async with async_session_maker() as session:
            stmt = insert(models.PrivateMessage).values(sender_id=sender_id, recipient_id=recipient_id,messages=messages,
                                                        is_read=is_read, fileUrl=file, id_return=id_return
                                                        )
            result = await session.execute(stmt)
            await session.commit()
            
            message_id = result.inserted_primary_key[0]
            return message_id