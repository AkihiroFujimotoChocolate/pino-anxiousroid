from urllib import response
import uuid
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import shutil
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.constants import LOG_LEVEL, MAX_RESPONSE_LENGTH
from app.utils.additional_rules import search_additional_rules
from app.utils.normalization import truncate_text
from app.utils.terminology import search_terminology
from app.utils.claude import generate_response
from app.utils.models import ChatMessage, ChatRole, TermCategory

# Environment variables for conversation history
CONV_HISTORY_PATH_TEMPLATE = os.getenv("CONV_HISTORY_PATH_TEMPLATE", "data/conversations/{user_id}.jsonl")
MAX_CHAT_LOG_LENGTH = int(os.getenv("MAX_CHAT_LOG_LENGTH", "10"))
CONV_HISTORY_MAX_SIZE_MB = int(os.getenv("CONV_HISTORY_MAX_SIZE_MB", "50"))
CONV_HISTORY_ARCHIVE_FOLDER = os.getenv("CONV_HISTORY_ARCHIVE_FOLDER", "data/conversations/archive/")

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

def get_conversation_file_path(user_id: str) -> str:
    """Get the conversation file path for a user."""
    p = Path(os.path.expandvars(os.path.expanduser(CONV_HISTORY_PATH_TEMPLATE.format(user_id=user_id))))
    return str(p)


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

        # Copy to archive
        shutil.copy(file_path, archive_path)

        # Truncate original file to last 2 * MAX_CHAT_LOG_LENGTH lines
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines[-2 * MAX_CHAT_LOG_LENGTH:])

    except Exception:
        # If archiving fails, continue silently to avoid breaking the chat
        pass


def load_conversation_history(user_id: str, max_length: int = MAX_CHAT_LOG_LENGTH) -> List[ChatMessage]:
    """Load conversation history for a user, limited to max_length messages."""
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

        # Return only the last max_length messages
        return messages[-max_length:]

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
        user_message = request.get_message_text()
        user_id = request.get_user_id()
        platform = request.get_platform()
        logger.info(f"received message from user {user_id} on platform {platform}: {user_message}(request_id: {request_id})")

        # Load conversation history for this user
        chat_history = load_conversation_history(user_id)
        logger.info(f"got chat history: {chat_history}(request_id: {request_id})")
        
        # Prepare parameters for Claude
        if len(chat_history) > 0:
            query = "".join([chat.content for chat in chat_history[-3:]]) + user_message
        else:
            query = user_message
        logger.info(f"got query for searching people: {query}(request_id: {request_id})")
        people = search_terminology(query, TermCategory.PERSON)
        logger.info(f"searched people: {people}(request_id: {request_id})")
        query = query + "".join([person.description for person in people])
        logger.info(f"got query for searching additional rules: {query}(request_id: {request_id})")
        additional_rules = search_additional_rules(query)
        logger.info(f"searched additional rules: {additional_rules}(request_id: {request_id})")
        params = {
            "people": people,
            "additional_rules": additional_rules
        }

        # Call Claude API through existing generate_response function with history
        reply, usage = generate_response(user_message, chat_history=chat_history, params=params)
        logger.info(f"generated reply: {reply}(request_id: {request_id})")
        logger.info(f"claude usage: {usage}(request_id: {request_id})")

        reply = reply.strip()

        reply = truncate_text(reply, MAX_RESPONSE_LENGTH) or truncate_text(reply, MAX_RESPONSE_LENGTH*2, 1) or reply

        # Save the incoming user message
        save_conversation_message(user_id, platform, "user", user_message)
        logger.info(f"saved user message from user {user_id} on platform {platform}: {user_message}(request_id: {request_id})")
        # Save the assistant response
        save_conversation_message(user_id, platform, "assistant", reply)
        logger.info(f"saved assistant message for user {user_id} on platform {platform}: {reply}(request_id: {request_id})")
        
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