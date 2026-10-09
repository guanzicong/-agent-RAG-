"""统一加载 config/ 目录下的 YAML 配置与环境变量。"""
import yaml
from dotenv import load_dotenv

from utils.path_tool import get_abs_path

# 启动时加载项目根目录 .env 并注入环境变量。
# override=False（默认）：系统已存在的同名变量优先；
# 若希望 .env 强制覆盖系统变量，可改为 override=True。
load_dotenv(get_abs_path(".env"), encoding="utf-8")


def load_rag_config(config_path: str = get_abs_path("config/rag.yml"), encoding: str = "utf-8"):
    """加载模型配置（rag.yml）。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = get_abs_path("config/chroma.yml"), encoding: str = "utf-8"):
    """加载向量库配置（chroma.yml）。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_prompts_config(config_path: str = get_abs_path("config/prompts.yml"), encoding: str = "utf-8"):
    """加载提示词路径配置（prompts.yml）。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = get_abs_path("config/agent.yml"), encoding: str = "utf-8"):
    """加载智能体配置（agent.yml）。"""
    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


# 模块级配置对象，供其他模块直接导入使用
rag_conf = load_rag_config()
chroma_conf = load_chroma_config()
prompts_conf = load_prompts_config()
agent_conf = load_agent_config()


if __name__ == '__main__':
    print(rag_conf["chat_model_name"])
