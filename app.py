from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from config import (
    validate_config,
    VK_CONFIRMATION_TOKEN,
    VK_SECRET,
)
from db import init_db, delete_conversation_id
from openai_client import ask_openai
from vk_client import send_vk_message

app = FastAPI()

validate_config()
init_db()


def split_long_text(text: str, limit: int = 3500) -> list[str]:
    if len(text) <= limit:
        return [text]

    parts = []
    current = ""

    for paragraph in text.split("\n"):
        candidate = f"{current}\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                parts.append(current)

            if len(paragraph) <= limit:
                current = paragraph
            else:
                for i in range(0, len(paragraph), limit):
                    parts.append(paragraph[i:i + limit])
                current = ""

    if current:
        parts.append(current)

    return parts


@app.post("/vk/callback", response_class=PlainTextResponse)
async def vk_callback(request: Request):
    data = await request.json()
    print("VK EVENT:", data)

    # Проверка secret
    if data.get("secret") != VK_SECRET:
        return "forbidden"

    # Подтверждение сервера
    if data.get("type") == "confirmation":
        return VK_CONFIRMATION_TOKEN

    # Новое сообщение
    if data.get("type") == "message_new":
        message = data["object"]["message"]

        user_text = (message.get("text") or "").strip()
        peer_id = message.get("peer_id")
        from_id = message.get("from_id")

        try:
            if not user_text:
                send_vk_message(peer_id, "Я пока умею работать только с текстовыми сообщениями.")
                return "ok"

            if user_text.lower() == "/reset":
                delete_conversation_id(from_id)
                send_vk_message(peer_id, "Контекст диалога сброшен.")
                return "ok"

            answer = ask_openai(from_id, user_text)

            for chunk in split_long_text(answer):
                send_vk_message(peer_id, chunk)

        except Exception as e:
            print("ERROR:", e)
            try:
                send_vk_message(peer_id, "Ошибка сервера. Попробуй ещё раз.")
            except Exception as inner_e:
                print("VK SEND ERROR:", inner_e)

        return "ok"

    return "ok"