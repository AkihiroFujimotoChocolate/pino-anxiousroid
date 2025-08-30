import uuid
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from utils.claude import generate_response


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
        
        # Prepare parameters for Claude
        params = {
            "user_id": user_id,
            "platform": platform
        }
        
        # Call Claude API through existing generate_response function
        reply, usage = generate_response(user_text, chat_history=[], params=params)
        
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