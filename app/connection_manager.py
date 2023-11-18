from datetime import datetime
import json
from fastapi import WebSocket
from app.database import async_session_maker
from app import models
from sqlalchemy import insert
from typing import Dict, Tuple







       # Connecting Private Messages     
class ConnectionManagerPrivate:
    def __init__(self):
        self.active_connections: Dict[Tuple[int, int], WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int, recipient_id: int):
        await websocket.accept()
        self.active_connections[(user_id, recipient_id)] = websocket

    def disconnect(self, user_id: int, recipient_id: int):
        self.active_connections.pop((user_id, recipient_id), None)

    async def send_private_message(self, message: str, sender_id: int, recipient_id: int, user_name: str, avatar: str):
        sender_to_recipient = (sender_id, recipient_id)
        recipient_to_sender = (recipient_id, sender_id)
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_data = {
            "created_at": current_time,
            "sender_id": sender_id,
            "message": message,
            "user_name": user_name,
            "avatar": avatar,
        }
        
        message_json = json.dumps(message_data, ensure_ascii=False)
        
        if sender_to_recipient in self.active_connections:
            await self.active_connections[sender_to_recipient].send_text(message_json)

        if recipient_to_sender in self.active_connections:
            await self.active_connections[recipient_to_sender].send_text(message_json)
            
        # else:
        #     await self.notify_user(recipient_id, "New message")

        # Зберігаємо повідомлення в базі даних
        await self.add_private_message_to_database(message, sender_id, recipient_id)


    async def notify_user(self, user_id: int, notification_message: str):
        """
        Надсилає сповіщення користувачу.

        Args:
            user_id (int): ID користувача, якому потрібно надіслати сповіщення.
            notification_message (str): Текст сповіщення.
        """
        notification_data = {
            "type": "notification",
            "message": notification_message
        }

        notification_json = json.dumps(notification_data, ensure_ascii=False)

        # Перевіряємо, чи є користувач онлайн
        for (sender, recipient), websocket in self.active_connections.items():
            if recipient == user_id:
                # Користувач онлайн, надсилаємо сповіщення
                await websocket.send_text(notification_json)
                break  # Припиняємо цикл, якщо сповіщення відправлено
            

    @staticmethod
    async def add_private_message_to_database(message: str, sender_id: int, recipient_id: int):
        async with async_session_maker() as session:
            stmt = insert(models.PrivateMessage).values(messages=message, sender_id=sender_id, recipient_id=recipient_id)
            await session.execute(stmt)
            await session.commit()