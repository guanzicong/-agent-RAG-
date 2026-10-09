from langchain_chroma import Chroma
from langchain_core.documents import Document
from utils.config_handler import chroma_conf
from model.model_factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
import os


class VectorStoreService:
    """向量库服务：负责文档入库、文本分片与检索。"""

    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators=chroma_conf["separators"],
            length_function=len,
        )

    def get_retriever(self):
        """返回向量检索器。"""
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """读取数据目录下的文档，分片后写入向量库，并借助 MD5 去重避免重复入库。"""

        def check_md5_hex(md5_for_check: str) -> bool:
            """判断该 MD5 是否已处理过。"""
            abs_path = get_abs_path(chroma_conf["md5_hex_store"])
            if not os.path.exists(abs_path):
                # MD5 记录文件不存在则先创建，并按"未处理过"返回
                open(abs_path, "w", encoding="utf-8").close()
                return False

            with open(abs_path, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    if line.strip() == md5_for_check:
                        return True

            return False

        def save_md5_hex(md5_for_check: str):
            """记录已处理的文件 MD5。"""
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str) -> list[Document]:
            """按文件后缀选择对应的加载器。"""
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            return []

        # 数据目录下所有允许类型的文件
        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            md5_hex = get_file_md5_hex(path)

            # 已入库过的文件直接跳过，避免重复写入
            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[加载知识库]{path}内没有有效文本内容，跳过")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[加载知识库]{path}分片后没有有效文本内容，跳过")
                    continue

                self.vector_store.add_documents(split_document)

                # 记录已处理的 MD5，下次加载即可跳过该文件
                save_md5_hex(md5_hex)

                logger.info(f"[加载知识库]{path} 内容加载成功")
            except Exception as e:
                # exc_info=True 会额外记录完整报错堆栈，False 则只记录报错信息本身
                logger.error(f"[加载知识库]{path}加载失败：{str(e)}", exc_info=True)
                continue


if __name__ == '__main__':
    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()

    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print("-"*20)


