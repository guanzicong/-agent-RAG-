"""为整个工程提供统一的绝对路径。"""
import os


def get_project_root() -> str:
    """获取工程根目录。

    :return: 工程根目录的绝对路径字符串
    """
    # __file__ 为当前文件路径，向上两级即是工程根目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_abs_path(relative_path: str) -> str:
    """将相对路径转换为基于工程根目录的绝对路径。

    :param relative_path: 相对工程根目录的路径
    :return: 绝对路径
    """
    return os.path.join(get_project_root(), relative_path)


if __name__ == '__main__':
    from utils.config_handler import chroma_conf
    print(get_abs_path(chroma_conf["persist_directory"]))
