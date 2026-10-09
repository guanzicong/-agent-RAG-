"""Agent 中间件：工具调用监控、模型调用日志、提示词动态切换。"""
from typing import Callable

from langchain.agents import AgentState
from langchain.agents.middleware import ModelRequest, before_model, dynamic_prompt, wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime
from langgraph.types import Command

from utils.logger_handler import logger
from utils.prompt_loader import load_report_prompts, load_system_prompts


@wrap_tool_call
def monitor_tool(
        # 本次工具调用的请求封装
        request: ToolCallRequest,
        # 真正执行工具的处理函数
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """工具执行监控：记录调用日志，并在特定工具调用时注入会话 ID / 切换场景。"""
    logger.info(f"[tool monitor]执行工具：{request.tool_call['name']}")
    logger.info(f"[tool monitor]传入参数：{request.tool_call['args']}")

    try:
        # 记忆功能：为 rag_summarize 自动注入当前会话 ID
        if request.tool_call['name'] == "rag_summarize":
            session_id = request.runtime.context.get("session_id", "user1")
            request.tool_call['args']['session_id'] = session_id
            logger.info(f"[tool monitor]已注入会话ID：{session_id}")

        result = handler(request)
        logger.info(f"[tool monitor]工具{request.tool_call['name']}调用成功")

        # fill_context_for_report 被调用即视为进入报告生成场景，后续提示词将随之切换
        if request.tool_call['name'] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(f"工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e


@before_model
def log_before_model(
        state: AgentState,      # 智能体的完整状态记录
        runtime: Runtime,       # 整个执行过程的上下文信息
):
    """模型调用前输出日志。"""
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")

    logger.debug(f"[log_before_model]{type(state['messages'][-1]).__name__} | {state['messages'][-1].content.strip()}")

    return None


@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    """生成提示词前动态选择：报告场景用报告提示词，其余用系统提示词。"""
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompts()

    return load_system_prompts()
