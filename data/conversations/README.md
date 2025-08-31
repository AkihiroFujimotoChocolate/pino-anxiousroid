# Conversation History Files

This directory contains conversation history files in JSONL format.

- Each user has their own conversation file: `{user_id}.jsonl`
- When files exceed the configured size limit, they are archived to the `archive/` subdirectory
- Files are automatically created when users start conversations

The conversation history is used to provide context to Claude for more coherent conversations.