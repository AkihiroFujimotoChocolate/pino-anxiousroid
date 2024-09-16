

def truncate_text(text: str, max_length: int,  max_sentences: int | None = None) -> str | None:
    
    truncated = text[:max_length]
    boundaries = ['.', '?', '!', '。', '？', '！', '\n', '\r\n']
    
    sentence_positions = []

    for i, char in enumerate(truncated):
        if char in boundaries:
            sentence_positions.append(i + 1)  
            if max_sentences and len(sentence_positions) == max_sentences:
                break
    
    if sentence_positions:
        return truncated[:sentence_positions[-1]]
    return None