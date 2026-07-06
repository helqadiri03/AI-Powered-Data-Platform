from pydantic import BaseModel
from typing import List

class RAGRequest(BaseModel):
    question: str

class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
