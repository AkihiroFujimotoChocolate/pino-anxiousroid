from enum import StrEnum

from pydantic import BaseModel

class ClaudeOptions(BaseModel):
    max_tokens: int
    temperature: float
    model: str

class ClaudeUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    elapsed_time_ms: int
    
class ChatRole(StrEnum):
    USER = "user"
    AI = "ai"
    
class ChatMessage(BaseModel):
    role: ChatRole
    content: str

class TermCategory(StrEnum):
    PERSON = "person"
    OTHER = "other"

class TermAttribute(BaseModel):
    name: str
    value: str

class Term(BaseModel):
    index_regex: str
    name: str
    categories: list[TermCategory]
    description: str
    alias: str
    flags: list[object] = []
    attributes: list[TermAttribute]

class AditionalRule(BaseModel):
    index_regex: str
    rules: list[str]