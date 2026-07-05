from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        examples=["Top 5 customers by total revenue"],
        description="A natural-language question about the e-commerce data.",
    )


class QueryResponse(BaseModel):
    question: str
    sql: str
    model_used: str
    columns: list[str]
    rows: list[list]
    row_count: int


class ErrorResponse(BaseModel):
    detail: str
