"""模型工厂：统一创建聊天模型与嵌入模型实例。"""
import os
from abc import ABC, abstractmethod
from typing import Optional

from langchain_community.chat_models.tongyi import BaseChatModel, ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.embeddings import Embeddings

from utils.config_handler import rag_conf

# 导入 config_handler 时会加载 .env，此处校验 DashScope Key 是否就绪
if not os.getenv("DASHSCOPE_API_KEY"):
    raise RuntimeError("未配置 DASHSCOPE_API_KEY：请在项目根目录 .env 中填写后重新启动")


class BaseModelFactory(ABC):
    """模型工厂抽象基类。"""

    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        """创建并返回模型实例。"""
        pass


class ChatModelFactory(BaseModelFactory):
    """聊天模型工厂。"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model=rag_conf["chat_model_name"])


class EmbeddingsFactory(BaseModelFactory):
    """嵌入模型工厂。"""

    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model=rag_conf["embedding_model_name"])


# 全局模型实例，供其他模块直接导入使用
chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
