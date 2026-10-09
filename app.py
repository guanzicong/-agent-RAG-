"""Streamlit 前端入口：提供「智扫通机器人智能客服」对话界面。"""
import time
import uuid

import streamlit as st

from agent.react_agent import ReactAgent

st.title("智扫通机器人智能客服")
st.divider()

# 智能体只创建一次，后续复用
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

# ===== 记忆功能：为当前浏览器会话生成唯一会话 ID =====
# st.session_state 在页面刷新后保留、浏览器关闭后重建，
# 因此「同一浏览器持续使用 = 同一会话共享记忆」
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())

if "message" not in st.session_state:
    st.session_state["message"] = []

# 回显历史消息
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    response_messages = []

    def capture(generator, cache_list):
        """边缓存完整回复、边逐字输出，实现打字机效果。"""
        for chunk in generator:
            cache_list.append(chunk)

            for char in chunk:
                time.sleep(0.01)
                yield char

    with st.spinner("智能客服思考中..."):
        # 传入当前浏览器会话的 session_id，Agent 按会话读写对话历史
        res_stream = st.session_state["agent"].execute_stream(prompt, st.session_state["session_id"])

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()
