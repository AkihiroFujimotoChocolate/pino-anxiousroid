# pino-anxiousroid
## Example of Environment Variables for Local Execution
Create a .env file in app directory as follows
```shell
CLAUDE_API_KEY=your_claude_api_kye
LOG_LEVEL=DEBUG
HASHED_ACCESS_TOKENS=xxxx
HASHED_INDEFINITE_ACCESS_TOKENS=xxx
IS_CLOSED=false

# Conversation History Configuration (optional)
CONV_HISTORY_PATH_TEMPLATE=data/conversations/{user_id}.jsonl
MAX_CHAT_LOG_LENGTH=10
CONV_HISTORY_MAX_SIZE_MB=50
CONV_HISTORY_ARCHIVE_FOLDER=data/conversations/archive/
```

### Conversation History Environment Variables

- `CONV_HISTORY_PATH_TEMPLATE`: Path template for conversation history files. Use `{user_id}` as placeholder. Default: `data/conversations/{user_id}.jsonl`
- `MAX_CHAT_LOG_LENGTH`: Number of messages from history to use for Claude responses. Default: `10`
- `CONV_HISTORY_MAX_SIZE_MB`: Maximum file size (MB) before archiving old conversation files. Default: `50`
- `CONV_HISTORY_ARCHIVE_FOLDER`: Path to archive folder for old conversation history files. Default: `data/conversations/archive/`

### Conversation History File Format

The conversation history is stored in JSONL (JSON Lines) format. Each line contains a single conversation message:

```json
{"user_id": "user123", "platform": "discord", "timestamp": "2024-01-01T12:00:00Z", "role": "user", "text": "Hello"}
{"user_id": "user123", "platform": "discord", "timestamp": "2024-01-01T12:00:01Z", "role": "assistant", "text": "Hello! How can I help you?"}
```

**Field Descriptions:**
- `user_id`: User identifier from the request
- `platform`: Platform identifier from the request origin
- `timestamp`: ISO 8601 UTC timestamp with 'Z' suffix
- `role`: Either "user" or "assistant"
- `text`: The message content

**Archiving Behavior:**
When a conversation file exceeds the configured maximum size, it is automatically moved to the archive folder with a timestamp suffix (e.g., `user123_20240101_120000.jsonl`). A new conversation file is then created for ongoing conversations.

## How to Run on Windows
1. Create a python v3.11 virtual environment in your project directory
```powershell
python3.11 -m venv .venv
```
2. Activate the virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```
3. While the virtual environment is active, install the required packages
```powershell
pip install -r requirements.txt
```
4. Run the Streamlit App
```powershell
streamlit run ./app/main.py
```

## How to Run on Linux
1. Create a python v3.11 virtual environment in your project directory
```shell
python3.11 -m venv .venv
```
2. Activate the virtual environment
```shell
source .venv/bin/activate
```
3. While the virtual environment is active, install the required packages
```shell
pip install -r requirements.txt
```
4. Run the Streamlit App
```shell
streamlit run ./app/main.py
```

## Web API Endpoint

This application also provides a FastAPI-based Web API endpoint for chat functionality.

### Running the API Server

To start the API server:

```shell
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Start the FastAPI server
python -m uvicorn app.api:app --reload --env-file app/.env
```

The API server will start on `http://localhost:8000`

### Testing the API Endpoint

**Endpoint**: `POST /api/chat/v0.1`

**Request Format**:
```json
{
  "request_id": "optional-unique-id",
  "origin": {
    "platform": "web"
  },
  "author": {
    "user_id": "user123"
  },
  "message": {
    "text": "こんにちは"
  }
}
```

**Response Format**:
```json
{
  "request_id": "optional-unique-id",
  "status": "ok",
  "messages": ["ぴのと申します。こんにちはですわ！"],
  "fallback_used": false
}
```

**Example using curl**:
```shell
curl -X POST "http://localhost:8000/api/chat/v0.1" \
  -H "Content-Type: application/json" \
  -d '{
    "author": {"user_id": "test_user"},
    "message": {"text": "Hello!"}
  }'
```

**Health Check**:
```shell
curl http://localhost:8000/health
```

### API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
