from typing import List
from langchain_core.documents import Document
from app.knowledge.structure_aware_chunking import structure_chunk
from pathlib import Path
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


# 持久化向量库
PERSIST_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION_NAME = "knowledge"


class KnowledgeService:
    def __init__(self):
        self.embeddings_model = OllamaEmbeddings(model="bge-m3")

    @staticmethod
    def _load_and_chunk(md_path: str):
        """读取原始 md 并按标题结构切块。"""
        text = Path(md_path).read_text(encoding="utf-8")
        return structure_chunk(text, split_level=2)

    def build(self, md_path: str):
        """构建向量库并持久化到磁盘（只在首次或文档更新时调用）。"""
        docs = self._load_and_chunk(md_path)
        documents = [
            Document(page_content=c["text"], metadata=c["meta"]) for c in docs
        ]
        # from_documents + persist_directory：向量自动落盘
        Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings_model,
            persist_directory=PERSIST_DIR,
            collection_name=COLLECTION_NAME,
        )

    def get_vectorstore(self) -> Chroma:
        """加载磁盘上已存在的向量库（不重复写入）。"""
        print("已加载向量库")
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings_model,
            persist_directory=PERSIST_DIR,
        )

    def search(self, query: str, k: int = 3) -> List[Document]:
        """从已落盘的向量库检索。"""
        retriever = self.get_vectorstore().as_retriever(search_kwargs={"k": k})
        return retriever.invoke(query)


if __name__ == "__main__":
    service = KnowledgeService()

    # 首次（或 md 有更新时）才建库落盘；之后这行可注释掉
    service.build("E:/笔记/我的脑图/AI应用开发学习/提示词模板范例.md")

    # 之后每次运行直接加载磁盘向量检索
    for doc in service.search("智能体里怎么使用提示词"):
        print(doc.page_content, "\n---")