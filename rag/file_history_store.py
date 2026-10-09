"""基于本地文件的会话记忆存储。"""
import json
import os
from typing import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

from utils.path_tool import get_abs_path


def get_history(session_id: str) -> "FileChatMessageHistory":
    """获取指定会话的记忆对象（文件存放于 chat_history/ 目录）。"""
    return FileChatMessageHistory(session_id, get_abs_path("chat_history"))


class FileChatMessageHistory(BaseChatMessageHistory):
    """将会话消息以 JSON 文件形式持久化。"""

    def __init__(self, session_id: str, storage_path: str):
        self.session_id = session_id        # 会话 ID
        self.storage_path = storage_path    # 存放各会话文件的目录
        self.file_path = os.path.join(self.storage_path, self.session_id)

        # 确保存放目录存在
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        """追加消息并整体落盘。

        :param messages: 新增消息序列（list、tuple 等均可）
        """
        all_messages = list(self.messages)      # 已有消息
        all_messages.extend(messages)           # 与新增消息合并

        # 消息对象无法直接写文件，先转为字典再以 JSON 序列化
        new_messages = [message_to_dict(message) for message in all_messages]

        # ensure_ascii=False：中文以明文保存，便于直接查看历史记录
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f, ensure_ascii=False, indent=2)

    @property
    def messages(self) -> list[BaseMessage]:
        """读取文件中的历史消息（@property 使其可当作属性访问）。"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                messages_data = json.load(f)    # 文件内容为 list[字典]
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            # 文件损坏（如写入中途被中断）时按空历史处理，避免整个会话不可用
            return []

    def clear(self) -> None:
        """清空当前会话的历史消息。"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([], f)
