# pino-anxiousroid
## Example of Environment Variables for Local Execution
Create a .env file in app directory as follows
```shell
CLAUDE_API_KEY=your_claude_api_kye
LOG_LEVEL=DEBUG
HASHED_ACCESS_TOKENS=xxxx
HASHED_INDEFINITE_ACCESS_TOKENS=xxx
IS_CLOSED=false
```

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
cd app
python api.py
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
