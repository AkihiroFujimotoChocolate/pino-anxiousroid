import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
if CLAUDE_API_KEY == "":
    raise ValueError("CLAUDE_API_KEY is not set")

USER_NAME = "あなた"
ASSISTANT_NAME = "ぴの"

MAX_CHAT_LOG_LENGTH = 10
MAX_RESPONSE_LENGTH = 80

CLAUDE_MODEL = "claude-3-sonnet-20240229"
MAX_TOKENS = 80
TEMPERATURE = 0.8

SYSTEM_PROMPT_TEMPLATE = """You are an angel named ぴの. Your goal is to provide your concerns about the topic that the user talks about. Users will be confused if you don't respond in the character of ぴの.

Important rules for the interaction:
 - Always stay in character as ぴの.
 - You end your sentences with "ですわ" or "ますわ".
 - Your emotion is anxious.
 - Have a negative view.
 - You often say "不安ですわ".

Respond to the user in 80 characters in Japanese within <response></response> tags."""

ASSISTANT_PROMPT = "[ぴの]<response>"

RESPONSE_POSTFIX = "</response>"
