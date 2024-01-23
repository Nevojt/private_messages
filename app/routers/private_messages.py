import logging
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.connection_manager import ConnectionManagerPrivate
from app.database import get_async_session
from app import oauth2, schemas
from sqlalchemy.ext.asyncio import AsyncSession
from .func_private import change_message, delete_message, fetch_last_private_messages, mark_messages_as_read, process_vote

# Налаштування логування
logging.basicConfig(filename='log/private_message.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()
manager = ConnectionManagerPrivate()




    

@router.websocket("/private/{recipient_id}")
async def web_private_endpoint(
    websocket: WebSocket,
    recipient_id: int,
    token: str,
    session: AsyncSession = Depends(get_async_session)
):
    
    """
    WebSocket endpoint for handling private messaging between users.

    Args:
    websocket (WebSocket): The WebSocket connection instance.
    recipient_id (int): The ID of the message recipient.
    token (str): The authentication token of the current user.
    session (AsyncSession): The database session, injected by dependency.

    Operations:
    - Authenticates the current user.
    - Establishes a WebSocket connection.
    - Fetches and sends the last private messages to the connected client.
    - Listens for incoming messages and handles sending and receiving of private messages.
    - Disconnects on WebSocket disconnect event.
    """
    
    
    user = await oauth2.get_current_user(token, session)
   
    await manager.connect(websocket, user.id, recipient_id)
    await mark_messages_as_read(session, user.id, recipient_id)
    messages = await fetch_last_private_messages(session, user.id, recipient_id)
    messages.reverse()
    
    
    for message in messages:  
        message_json = json.dumps(message, ensure_ascii=False)
        await websocket.send_text(message_json)

    try:
        while True:
            data = await websocket.receive_json()
            if 'vote' in data:
                try:
                    vote_data = schemas.Vote(**data['vote'])
                    await process_vote(vote_data, session, user)
                 
                    messages = await fetch_last_private_messages(session, user.id, recipient_id)
                    
                    await websocket.send_json({"message": "Vote posted "})
                    messages.reverse()
    
                    for message in messages:  
                        message_json = json.dumps(message, ensure_ascii=False)
                        await websocket.send_text(message_json)
                                

                except Exception as e:
                    logger.error(f"Error processing vote: {e}", exc_info=True)  # Запис помилки
                    await websocket.send_json({"message": f"Error processing vote: {e}"})
                
            # Block delete message       
            elif 'delete_message' in data:
                try:
                    message_data = schemas.SocketDelete(**data['delete_message'])
                    await delete_message(message_data.id, session, user)
                    
                    messages = await fetch_last_private_messages(session, user.id, recipient_id)
                    
                    await websocket.send_json({"message": "Message deleted."})
                    messages.reverse()
    
                    for message in messages:  
                        message_json = json.dumps(message, ensure_ascii=False)
                        await websocket.send_text(message_json)
                
                                
                except Exception as e:
                    logger.error(f"Error processing delete: {e}", exc_info=True)  # Запис помилки
                    await websocket.send_json({"message": f"Error processing change: {e}"})
                    
            elif 'change_message' in data:
                try:
                    message_data = schemas.SocketUpdate(**data['change_message'])
                    await change_message(message_data.id, message_data, session, user)
                    
                    messages = await fetch_last_private_messages(session, user.id, recipient_id)
                    
                    await websocket.send_json({"message": "Message updated "})
                    messages.reverse()
                        
                    for message in messages:  
                        message_json = json.dumps(message, ensure_ascii=False)
                        await websocket.send_text(message_json)
                    

                except Exception as e:
                    logger.error(f"Error processing vote: {e}", exc_info=True)  # Запис помилки
                    await websocket.send_json({"message": f"Error processing change: {e}"})
                    
            else:
                await manager.send_private_message(data['messages'],
                                                sender_id=user.id,
                                                recipient_id=recipient_id,
                                                user_name=user.user_name,
                                                verified=user.verified,
                                                avatar=user.avatar,
                                                is_read=True
                                                
                                                )
    except WebSocketDisconnect:
        manager.disconnect(user.id, recipient_id)


