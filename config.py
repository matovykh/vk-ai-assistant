import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROMPT_ID = os.getenv("OPENAI_PROMPT_ID")

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_CONFIRMATION_TOKEN = os.getenv("VK_CONFIRMATION_TOKEN")
VK_SECRET = os.getenv("VK_SECRET")
VK_API_VERSION = os.getenv("VK_API_VERSION", "5.199")

APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))


def validate_config():
    required = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "OPENAI_PROMPT_ID": OPENAI_PROMPT_ID,
        "VK_GROUP_TOKEN": VK_GROUP_TOKEN,
        "VK_CONFIRMATION_TOKEN": VK_CONFIRMATION_TOKEN,
        "VK_SECRET": VK_SECRET,
    }

    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(
            f"Не заполнены переменные окружения: {', '.join(missing)}"
        )