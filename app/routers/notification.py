from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from app.connection_manager import ConnectionManagerNotification
from app.database import get_async_session
from app import models, oauth2
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
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
    messages = new_messages.scalars().all()
    
    # Отримання sender_id для кожного повідомлення
    messages_info = [{"sender_id": message.sender_id, "message_id": message.id} for message in messages]
    return messages_info
    

@router.websocket("/notification")
async def web_private_notification(
    websocket: WebSocket,
    token: str,
    session: AsyncSession = Depends(get_async_session)
):
    try:
        user = await oauth2.get_current_user(token, session)
    except Exception as e:
        await websocket.close(code=1008)  # Код закриття для політики
        return  # Припиняємо подальше виконання

    await manager.connect(websocket, user.id)

    try:
        while True:
            # Перевіряємо статус WebSocket перед відправкою повідомлень
            if websocket.client_state != WebSocketState.CONNECTED:
                break  # Припиняємо цикл, якщо з'єднання не активне

            new_messages_info = await check_new_messages(session, user.id)
            if new_messages_info:
                for message_info in new_messages_info:
                    await websocket.send_json({
                        "type": "new_message",
                        "sender_id": message_info["sender_id"],
                        "message_id": message_info["message_id"]
                    })

            await asyncio.sleep(5)  # N секунд чекання, можна налаштувати
    except WebSocketDisconnect:
        manager.disconnect(user.id)
    except Exception as e:
        # Логування помилки
        print(f"Error in WebSocket: {e}")
        await websocket.close(code=1011)  # Несподівана помилка

