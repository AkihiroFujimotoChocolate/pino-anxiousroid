import uuid
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from utils.claude import generate_response
from utils.models import ChatMessage, ChatRole

# Environment variables for conversation history
CONV_HISTORY_PATH_TEMPLATE = os.getenv("CONV_HISTORY_PATH_TEMPLATE", "data/conversations/{user_id}.jsonl")
MAX_CHAT_LOG_LENGTH = int(os.getenv("MAX_CHAT_LOG_LENGTH", "10"))
CONV_HISTORY_MAX_SIZE_MB = int(os.getenv("CONV_HISTORY_MAX_SIZE_MB", "50"))
CONV_HISTORY_ARCHIVE_FOLDER = os.getenv("CONV_HISTORY_ARCHIVE_FOLDER", "data/conversations/archive/")


def get_conversation_file_path(user_id: str) -> str:
    """Get the conversation file path for a user."""
    return CONV_HISTORY_PATH_TEMPLATE.format(user_id=user_id)


def ensure_directory_exists(file_path: str):
    """Ensure the directory for the file path exists."""
    directory = Path(file_path).parent
    directory.mkdir(parents=True, exist_ok=True)


def archive_conversation_file(file_path: str, user_id: str):
    """Archive conversation file if it exists and exceeds size limit."""
    try:
        if not Path(file_path).exists():
            return
            
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        if file_size_mb < CONV_HISTORY_MAX_SIZE_MB:
            return
            
        # Create archive directory
        archive_dir = Path(CONV_HISTORY_ARCHIVE_FOLDER)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"{user_id}_{timestamp}.jsonl"
        archive_path = archive_dir / archive_filename
        
        # Move file to archive
        Path(file_path).rename(archive_path)
        
    except Exception:
        # If archiving fails, continue silently to avoid breaking the chat
        pass


def load_conversation_history(user_id: str) -> List[ChatMessage]:
    """Load conversation history for a user, limited to MAX_CHAT_LOG_LENGTH messages."""
    file_path = get_conversation_file_path(user_id)
    
    if not Path(file_path).exists():
        return []
    
    try:
        messages = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                data = json.loads(line)
                role = ChatRole.USER if data['role'] == 'user' else ChatRole.AI
                messages.append(ChatMessage(role=role, content=data['text']))
        
        # Return only the last MAX_CHAT_LOG_LENGTH messages
        return messages[-MAX_CHAT_LOG_LENGTH:]
        
    except Exception:
        # If loading fails, return empty history to avoid breaking the chat
        return []


def save_conversation_message(user_id: str, platform: str, role: str, text: str):
    """Save a conversation message to the user's history file."""
    try:
        file_path = get_conversation_file_path(user_id)
        
        # Archive if file is too large before adding new message
        archive_conversation_file(file_path, user_id)
        
        # Ensure directory exists
        ensure_directory_exists(file_path)
        
        # Create message object
        message_data = {
            "user_id": user_id,
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "role": role,
            "text": text
        }
        
        # Append to file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(message_data, ensure_ascii=False) + '\n')
            
    except Exception:
        # If saving fails, continue silently to avoid breaking the chat
        pass


class ChatRequest(BaseModel):
    request_id: Optional[str] = Field(default=None, description="Unique id for tracing; echoed if provided")
    origin: Optional[dict] = Field(default=None)
    author: dict = Field(..., description="Author information with user_id")
    message: dict = Field(..., description="Message with text content")

    def get_platform(self) -> str:
        """Get platform from origin, default to 'unknown'"""
        if self.origin and "platform" in self.origin:
            return self.origin["platform"]
        return "unknown"

    def get_user_id(self) -> Optional[str]:
        """Get user_id from author"""
        return self.author.get("user_id")

    def get_message_text(self) -> str:
        """Get text from message"""
        return self.message["text"]


class ErrorInfo(BaseModel):
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class ChatResponse(BaseModel):
    request_id: Optional[str] = Field(default=None, description="Mirrors the request id when provided")
    status: str = Field(..., description="Status: ok or provider_error")
    messages: List[str] = Field(..., description="Response messages")
    fallback_used: Optional[bool] = Field(default=False, description="True when fallback text is used")
    error: Optional[ErrorInfo] = Field(default=None, description="Error information when status is provider_error")


app = FastAPI(title="Pino Anxiousroid API", version="0.1")


@app.post("/api/chat/v0.1", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns AI responses.
    """
    # Generate request_id if not provided
    request_id = request.request_id or str(uuid.uuid4())
    
    try:
        # Extract required fields
        user_text = request.get_message_text()
        user_id = request.get_user_id()
        platform = request.get_platform()
        
        # Load conversation history for this user
        chat_history = load_conversation_history(user_id)
        
        # Save the incoming user message
        save_conversation_message(user_id, platform, "user", user_text)
        
        # Prepare parameters for Claude
        params = {
            "user_id": user_id,
            "platform": platform
        }
        
        # Call Claude API through existing generate_response function with history
        reply, usage = generate_response(user_text, chat_history=chat_history, params=params)
        
        # Save the assistant response
        save_conversation_message(user_id, platform, "assistant", reply)
        
        # Return successful response
        return ChatResponse(
            request_id=request_id,
            status="ok",
            messages=[reply],
            fallback_used=False
        )
        
    except Exception as e:
        # Return error response
        return ChatResponse(
            request_id=request_id,
            status="provider_error",
            messages=[],
            fallback_used=False,
            error=ErrorInfo(
                code="runtime_error",
                message=str(e)
            )
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)