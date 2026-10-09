# Demo of Agent — 扫地机器人智能客服

基于 LangChain / LangGraph 与通义千问构建的 ReAct 智能体示例：一个面向扫地机器人、扫拖一体机器人的智能客服，支持知识库检索问答、多轮对话记忆，以及用户使用报告生成。

## 功能特性

- **ReAct 智能体**：按「思考 → 行动 → 观察 → 再思考」流程自主调用工具回答问题
- **RAG 知识库问答**：对本地知识文档做向量检索，结合参考资料生成总结回答
- **多轮对话记忆**：按 `session_id` 将会话历史持久化到本地文件
- **报告生成**：借助中间件动态切换提示词，按固定流程生成用户使用报告
- **Streamlit 前端**：提供带打字机效果的对话界面

## 目录结构

```
.
├── app.py                    # Streamlit 前端入口
├── agent/
│   ├── react_agent.py        # ReAct 智能体：组合模型、提示词、工具与中间件
│   └── tools/
│       ├── agent_tools.py    # 本地工具定义（检索、用户信息、天气、外部数据等）
│       └── middleware.py     # 中间件：工具监控、模型日志、提示词切换
├── rag/
│   ├── rag_service.py        # RAG 检索 + 总结链路
│   ├── vector_store.py       # 向量库构建与检索
│   └── file_history_store.py # 基于文件的会话记忆
├── model/model_factory.py    # 模型工厂（聊天模型 / 嵌入模型）
├── utils/                    # 配置、日志、提示词加载、路径与文件工具
├── config/                   # YAML 配置
├── prompts/                  # 提示词文本
├── data/                     # 知识库原始文档（txt / pdf）
└── requirements.txt
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，填入 DashScope API Key：

```
DASHSCOPE_API_KEY=你的Key
```

### 3. 构建向量库

首次运行前需将 `data/` 下的文档写入向量库（已入库的文件会通过 MD5 去重自动跳过）：

```bash
python rag/vector_store.py
```

### 4. 启动应用

```bash
streamlit run app.py
```

## 配置说明

| 文件 | 说明 |
| --- | --- |
| `config/rag.yml` | 聊天模型与嵌入模型名称 |
| `config/chroma.yml` | 向量库、文本分片与检索参数 |
| `config/prompts.yml` | 各类提示词的文件路径 |
| `config/agent.yml` | 外部数据文件路径 |

## 说明

- `data/` 中仅有少量示例文档，实际使用可替换为自己的知识库文件。
- 工具 `get_weather`、`get_user_location` 返回**模拟数据**，接入真实服务时替换 `agent/tools/agent_tools.py` 中对应实现即可。
- 运行产物（`logs/`、`chat_history/`、`chroma_db/`、`md5.text`）与 `.env` 均已在 `.gitignore` 中忽略，不会提交到仓库。
