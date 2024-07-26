
from openai import AsyncOpenAI
from app.config import settings

from fastapi import FastAPI, HTTPException

app = FastAPI()

sayori_key=settings.openai_api_key

client = AsyncOpenAI(
    api_key=sayori_key
)

async def ask_to_gpt(ask_to_chat: str) -> None:
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": ask_to_chat,
            }
        ],
        model="gpt-4o-mini",
        temperature=0.9,
        max_tokens=100,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    response = chat_completion.choices[0].model_dump()
    return response["message"]["content"]








# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


