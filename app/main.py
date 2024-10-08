import streamlit as st
import uuid
import hashlib

from utils import generate_response
from utils import search_terminology
from utils import search_additional_rules
from utils import ChatMessage, ChatRole, TermCategory
from utils import truncate_text
from constants import USER_NAME, ASSISTANT_NAME, MAX_CHAT_LOG_LENGTH, TITLE, LOG_LEVEL,  HASHED_ACCESS_TOKENS, IS_CLOSED, HASHED_INDEFINITE_ACCESS_TOKENS, MAX_RESPONSE_LENGTH

from streamlit.logger import get_logger

logger = get_logger(__name__)
logger.setLevel(LOG_LEVEL)

access_token = st.query_params.get("token",None)
hashed_user_access_token = hashlib.sha256(access_token.encode()).hexdigest() if access_token is not None else None

if IS_CLOSED:
    if hashed_user_access_token is None or hashed_user_access_token not in HASHED_INDEFINITE_ACCESS_TOKENS:
        st.error(f"今回の {TITLE} 公開は終了しました。次回の公開をおたのしみに！ https://x.com/akkyron_main") 
        st.stop()

if hashed_user_access_token is None or hashed_user_access_token not in HASHED_ACCESS_TOKENS + HASHED_INDEFINITE_ACCESS_TOKENS:
    st.error("アクセス権がありません。")
    st.stop()

st.title(TITLE)


# チャットログを保存したセッション情報を初期化
if "chat_history" not in st.session_state:
    st.session_state.chat_history: list[ChatMessage] = []
    st.session_state.session_id = uuid.uuid4().hex
    
session_id = st.session_state.session_id


user_message = st.chat_input("メッセージを入力")
if user_message:
    logger.info(f"received message: {user_message}(session_id: {session_id})")
    for chat in st.session_state.chat_history:
        with st.chat_message(USER_NAME if chat.role == ChatRole.USER else ASSISTANT_NAME):
            st.write(chat.content)

    with st.chat_message(USER_NAME):
        st.write(user_message)

    chat_history = st.session_state.chat_history[-MAX_CHAT_LOG_LENGTH:]
    logger.info(f"got chat history: {chat_history}(session_id: {session_id})")
    
    if len(chat_history) > 0:
        query = "".join([chat.content for chat in chat_history[-3:]]) + user_message
    else:
        query = user_message
    logger.info(f"got query for searching people: {query}(session_id: {session_id})")
    people = search_terminology(query, TermCategory.PERSON)
    logger.info(f"searched people: {people}(session_id: {session_id})")
    query = query + "".join([person.description for person in people])
    logger.info(f"got query for searching additional rules: {query}(session_id: {session_id})")
    additional_rules = search_additional_rules(query)
    logger.info(f"searched additional rules: {additional_rules}(session_id: {session_id})")

    response, claude_usage = generate_response(user_message, chat_history=chat_history, params={"people": people, "additional_rules": additional_rules})
    logger.info(f"generated response: {response}(session_id: {session_id})")
    logger.info(f"claude usage: {claude_usage}(session_id: {session_id})")
    
    ai_message = truncate_text(response, MAX_RESPONSE_LENGTH) or truncate_text(response, MAX_RESPONSE_LENGTH*2, 1) or response
    with st.chat_message(ASSISTANT_NAME):
        st.write(ai_message)
        logger.info(f"sent message: {ai_message}(session_id: {session_id})")
    
    st.session_state.chat_history.append(ChatMessage(role=ChatRole.USER, content=user_message))
    st.session_state.chat_history.append(ChatMessage(role=ChatRole.AI, content=ai_message))
