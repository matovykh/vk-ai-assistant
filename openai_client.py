from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_PROMPT_ID
from db import get_conversation_id, save_conversation_id


client = OpenAI(api_key=OPENAI_API_KEY)


def get_or_create_conversation(vk_user_id: int) -> str:
    existing_id = get_conversation_id(vk_user_id)
    if existing_id:
        return existing_id

    conversation = client.conversations.create()
    conversation_id = conversation.id
    save_conversation_id(vk_user_id, conversation_id)
    return conversation_id


def ask_openai(vk_user_id: int, user_text: str) -> str:
    conversation_id = get_or_create_conversation(vk_user_id)

    response = client.responses.create(
        prompt={"id": OPENAI_PROMPT_ID},  # type: ignore[arg-type]
        conversation=conversation_id,
        input=user_text,
        include=["file_search_call.results"],
        context_management=[
            {
                "type": "compaction",
                "compact_threshold": 12000
            }
        ],
    )

    answer = response.output_text
    if not answer or not answer.strip():
        return "Не получилось сформировать ответ. Попробуй переформулировать вопрос."

    return answer.strip()