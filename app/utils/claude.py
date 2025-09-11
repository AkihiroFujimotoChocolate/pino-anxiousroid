from http import client
import time
from typing import Optional

import anthropic
import pystache

from app.constants import (
    CLAUDE_API_KEY, MAX_TOKENS, TEMPERATURE,
    SYSTEM_PROMPT_TEMPLATE, ASSISTANT_PROMPT_TEMPLATE, RESPONSE_POSTFIX, CLAUDE_MODEL
)
from .models import ClaudeOptions, ClaudeUsage, ChatRole, ChatMessage

client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def _call_claude_api(
    system_prompt: str, user_prompt: str,
    options: ClaudeOptions,
    chat_history: list[ChatMessage] = [],
    assistant_prompt: Optional[str] = None
) -> tuple[str, ClaudeUsage]:

    start_datetime = time.time()
    
    messages = []
    for chat in chat_history:
        messages.append({
            "role": "user" if chat.role == ChatRole.USER else "assistant",
            "content": [
                {
                    "type": "text",
                    "text": chat.content
                }
            ]
        })
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_prompt
            }
        ]
    })
    if assistant_prompt:
        messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": assistant_prompt
                }
            ]
        })
    
    response = client.messages.create(
        model=options.model,
        max_tokens=options.max_tokens,
        temperature=options.temperature,
        system=system_prompt,
        messages=messages
    )
    end_datetime = time.time()
    
    response_text = response.content[0].text
    response_usage = ClaudeUsage(
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        elapsed_time_ms=int((end_datetime - start_datetime) * 1000)
    )
    
    return response_text, response_usage

def generate_response(query: str, chat_history: list[ChatMessage] = [], params: dict = {}) -> tuple[str, ClaudeUsage]:
    options = ClaudeOptions(
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        model=CLAUDE_MODEL
    ) 
    system_prompt = pystache.render(SYSTEM_PROMPT_TEMPLATE, params)
    assistant_prompt = pystache.render(ASSISTANT_PROMPT_TEMPLATE, params)
    response_text, response_usage = _call_claude_api(
        system_prompt=system_prompt,
        user_prompt=query,
        options=options,
        chat_history=chat_history,
        assistant_prompt=assistant_prompt
    )
    return response_text.rstrip(RESPONSE_POSTFIX), response_usage