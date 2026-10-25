from typing import List

from langchain.tools import tool
from app.knowledge.service import KnowledgeService
from langchain_core.documents import Document

knowledge = KnowledgeService()


@tool
def knowledge_search(query: str) -> List[Document]:
    """在知识库中搜索信息。"""
    return knowledge.search(query)



