import streamlit as st
from claude import generate_response
from models import ChatMessage, ChatRole
from constants import USER_NAME, ASSISTANT_NAME, MAX_CHAT_LOG_LENGTH


st.title("StreamlitのChatサンプル")


# チャットログを保存したセッション情報を初期化
if "chat_log" not in st.session_state:
    st.session_state.chat_log: list[ChatMessage] = []


user_msg = st.chat_input("メッセージを入力")
if user_msg:
    # 以前のチャットログを表示
    for chat in st.session_state.chat_log:
        with st.chat_message(USER_NAME if chat.role == ChatRole.USER else ASSISTANT_NAME):
            st.write(chat.content)

    # 最新のユーザメッセージを表示
    with st.chat_message(USER_NAME):
        st.write(user_msg)

    # アシスタントのメッセージを表示
    chat_log = st.session_state.chat_log[-MAX_CHAT_LOG_LENGTH:]
    response, _ = generate_response(user_msg, chat_log)
    with st.chat_message(ASSISTANT_NAME):
        assistant_msg = response
        assistant_response_area = st.empty()
        assistant_response_area.write(assistant_msg)

    # セッションにチャットログを追加
    st.session_state.chat_log.append(ChatMessage(role=ChatRole.USER, content=user_msg))
    st.session_state.chat_log.append(ChatMessage(role=ChatRole.AI, content=assistant_msg))
