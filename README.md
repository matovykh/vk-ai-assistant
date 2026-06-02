# VK AI Assistant 🤖

A chatbot for VK (VKontakte) communities powered by OpenAI. It receives user messages through the VK Callback API, forwards them to OpenAI, and returns responses while maintaining a separate conversation context for each user.

## ✨ Features

- 💬 Handles incoming messages from a VK community via Callback API
- 🧠 Maintains per-user dialog context (via OpenAI Conversations)
- 🔄 `/reset` command to clear the conversation context
- ✂️ Automatically splits long responses into chunks (VK message length limit)
- ⚙️ Configurable prompt (Prompt ID) — assistant logic is managed in the OpenAI Playground
- 🗜️ Automatic context compaction when the history grows too large

## 🏗️ Architecture

The project follows the separation-of-concerns principle:

| Module             | Responsibility                                               |
| ------------------ | ------------------------------------------------------------ |
| `app.py`           | FastAPI application. Receives VK webhooks, validates events, routes logic, and orchestrates calls to other modules |
| `openai_client.py` | OpenAI integration: creating/retrieving a conversation, sending a request, returning the response |
| `vk_client.py`     | Sends messages back to VK via the `messages.send` method     |
| `db.py`            | Storage layer (SQLite): maps `vk_user_id → conversation_id`  |
| `config.py`        | Loads and validates environment variables                    |

### Message processing flow



```
VK Callback API → /vk/callback → secret validation
   → confirmation / message_new
   → ask_openai(from_id, text) → OpenAI Responses API
   → split_long_text() → send_vk_message() → VK
```

## 🚀 Installation & Setup

### Requirements

- Python 3.10+
- A VK community with the Callback API enabled
- An OpenAI API key and a prompt created in the [OpenAI Playground](https://platform.openai.com/playground)

### Installation

bash



```bash
git clone https://github.com/your-username/vk-ai-assistant.git
cd vk-ai-assistant

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Example `requirements.txt`:



```
fastapi
uvicorn
openai
requests
python-dotenv
```

### Environment variables

Create a `.env` file in the project root:

env



```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_PROMPT_ID=pmpt_...

# VK
VK_GROUP_TOKEN=vk1.a...
VK_CONFIRMATION_TOKEN=abc123
VK_SECRET=your_secret_string
VK_API_VERSION=5.199

# Server
APP_HOST=127.0.0.1
APP_PORT=8000
```

| Variable                | Description                                          |
| ----------------------- | ---------------------------------------------------- |
| `OPENAI_API_KEY`        | OpenAI API access key                                |
| `OPENAI_PROMPT_ID`      | ID of the prompt created in the OpenAI Playground    |
| `VK_GROUP_TOKEN`        | VK community access token                            |
| `VK_CONFIRMATION_TOKEN` | String used to confirm the server in Callback API    |
| `VK_SECRET`             | Secret key used to verify the authenticity of events |
| `VK_API_VERSION`        | VK API version (defaults to `5.199`)                 |
| `APP_HOST` / `APP_PORT` | Server host and port                                 |

### Running

bash



```bash
uvicorn app:app --host 127.0.0.1 --port 8000
```

> To receive webhooks from VK, the server must be accessible over HTTPS. During development you can use a tunnel such as [ngrok](https://ngrok.com/).

## ⚙️ VK Callback API Setup

1. Go to **Manage Community → API Usage → Callback API**.
2. Set the server URL: `https://your-domain/vk/callback`.
3. Choose the API version matching `VK_API_VERSION`.
4. In the **Secret key** field, set the value of `VK_SECRET`.
5. Use the value of `VK_CONFIRMATION_TOKEN` as the server confirmation string.
6. Enable the **"Incoming message"** (`message_new`) event type.
7. Click **Confirm**.

## 🧠 Context Management

- A dedicated `conversation_id` (OpenAI Conversation) is created for each VK user and stored in SQLite.
- This allows the model to remember the user's previous messages.
- The **`/reset`** command deletes the stored `conversation_id` — the next dialog starts from scratch.
- When the history grows, the context is automatically compacted (`compaction`, threshold of 12,000 tokens).

## 🎛️ Prompt ID

The assistant's behavior (system instructions, model, tools such as `file_search`) is defined **not in the code** but in the OpenAI prompt, connected via `OPENAI_PROMPT_ID`.

Benefits:

- Change assistant logic **without editing code or redeploying**
- Centralized prompt versioning
- Clean application code (integration only)
- Convenient prompt debugging in the Playground

## 📁 Project Structure



```
.
├── app.py             # FastAPI app and VK event handling
├── openai_client.py   # OpenAI integration
├── vk_client.py       # Sending messages to VK
├── db.py              # SQLite operations
├── config.py          # Configuration and env validation
├── requirements.txt
├── .env               # Environment variables (do not commit!)
└── bot.db             # SQLite database (created automatically)
```

## 🔒 Security

- Never publish your `.env` file or tokens — add them to `.gitignore`.
- The `VK_SECRET` validation protects the endpoint from unauthorized requests.
- Use HTTPS for receiving webhooks.

Example `.gitignore`:



```
.env
bot.db
__pycache__/
venv/
```

## 📝 License

This project is distributed under the MIT License.