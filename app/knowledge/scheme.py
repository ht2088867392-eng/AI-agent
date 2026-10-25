from pydantic import BaseModel


class Knowledge(BaseModel):
    name: str      # 文档名
    content: str   # 文档内容
