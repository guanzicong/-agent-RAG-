"""文件相关工具：MD5 计算、目录扫描、文档加载。"""
import hashlib
import os

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

from utils.logger_handler import logger


def get_file_md5_hex(filepath: str) -> str | None:
    """计算文件的 MD5 十六进制字符串，用于知识库去重。

    :param filepath: 文件路径
    :return: MD5 十六进制字符串；文件不存在或计算失败时返回 None
    """
    if not os.path.exists(filepath):
        logger.error(f"[md5计算]文件{filepath}不存在")
        return None

    if not os.path.isfile(filepath):
        logger.error(f"[md5计算]路径{filepath}不是文件")
        return None

    md5_obj = hashlib.md5()

    chunk_size = 4096  # 每次读取 4KB，避免大文件一次性读入内存
    try:
        with open(filepath, "rb") as f:  # 以二进制方式读取
            while chunk := f.read(chunk_size):  # 海象运算符：先赋值再判断是否为文件末尾
                md5_obj.update(chunk)

        return md5_obj.hexdigest()
    except Exception as e:
        logger.error(f"计算文件{filepath}md5失败，{str(e)}")
        return None


def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    """列出目录下符合指定后缀的文件。

    :param path: 目录路径
    :param allowed_types: 允许的文件后缀元组，例如 ("txt", "pdf")
    :return: 文件绝对路径组成的元组
    """
    files = []

    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type]{path}不是文件夹")
        return ()  # 目录无效时返回空结果，避免把后缀名当文件路径返回

    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))

    return tuple(files)


def pdf_loader(filepath: str, passwd=None) -> list[Document]:
    """加载 PDF 文件为文档列表。"""
    return PyPDFLoader(filepath, passwd).load()


def txt_loader(filepath: str) -> list[Document]:
    """加载 UTF-8 编码的文本文件为文档列表。"""
    return TextLoader(filepath, encoding="utf-8").load()
