from enum import Enum

from pydantic import BaseModel

class ClaudeOptions(BaseModel):
    max_tokens: int
    temperature: float
    model: str

class ClaudeUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    elapsed_time_ms: int
    
class ChatRole(str, Enum):
    USER = "user"
    AI = "ai"
    
class ChatMessage(BaseModel):
    role: ChatRole
    content: str
