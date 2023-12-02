from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.connection_manager import ConnectionManagerNotification
from app.database import get_async_session
from app import models, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import asyncio

router = APIRouter()

manager = ConnectionManagerNotification()

async def check_new_messages(session: AsyncSession, user_id: int):
    """
    Перевіряє наявність нових повідомлень для користувача.

    Args:
        session (AsyncSession): Сесія бази даних.
        user_id (int): ID користувача.

    Returns:
        List[models.PrivateMessage]: Список нових повідомлень.
    """
    new_messages = await session.execute(
        select(models.PrivateMessage)
        .where(models.PrivateMessage.recipient_id == user_id, models.PrivateMessage.is_read == True)
    )
    return new_messages.scalars().all()

@router.websocket("/private/notification")
async def web_private_notification(
    websocket: WebSocket,
    token: str,
    session: AsyncSession = Depends(get_async_session)
):
    # user = await oauth2.get_current_user(token, session)
    try:
        user = await oauth2.get_current_user(token, session)
        print(user.id)
    except Exception as e:
        print("Error getting user")
        await websocket.close(code=1008)  # Код закриття для політики
        return  # Припиняємо подальше виконання
    await manager.connect(websocket, user.id)

    try:
        while True:
            # Перевіряємо нові повідомлення кожні N секунд
            new_messages = await check_new_messages(session, user.id)
            if new_messages:
                await websocket.send_json({"type": "new_message", "data": "You have new messages"})
            
            await asyncio.sleep(1)  # N секунд чекання, можна налаштувати
    except WebSocketDisconnect:
        manager.disconnect(user.id)
