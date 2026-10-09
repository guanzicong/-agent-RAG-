from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage

from model.model_factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_user_id, get_current_month,
                                     get_weather, get_user_location,
                                     fetch_external_data, fill_context_for_report)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch
from rag.file_history_store import get_history


class ReactAgent:
    """ReAct 智能体：组合本地工具、系统提示词与中间件，对外提供流式问答。"""

    def __init__(self):
        # 智能体可用的本地工具集合
        local_tools = [rag_summarize, get_user_id, get_current_month,
                       get_weather, get_user_location,
                       fetch_external_data, fill_context_for_report]

        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=local_tools,
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self, query: str, session_id: str = "default"):
        """流式执行一轮问答，逐段产出模型回复。

        :param query: 用户本轮提问
        :param session_id: 会话 ID，用于隔离多轮对话记忆
        """
        # 加载当前会话的历史消息（持久化在 chat_history/<session_id> 文件中）
        history = get_history(session_id)

        # 历史消息与本轮提问一并提交，使模型具备多轮对话上下文
        input_dict = {
            "messages": history.messages + [HumanMessage(content=query)],
        }

        latest_message = None
        for chunk in self.agent.stream(
                input_dict,
                stream_mode="values",
                context={"report": False, "session_id": session_id}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"

        # 仅保存干净的问答对：工具调用消息不入库，
        # 否则后续轮次会因 tool_calls / ToolMessage 配对缺失而报错
        if (isinstance(latest_message, AIMessage)
                and latest_message.content
                and not latest_message.tool_calls):
            history.add_messages([
                HumanMessage(content=query),
                AIMessage(content=latest_message.content),
            ])
