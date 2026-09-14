from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel

T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class PaginatedData(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

class PaginatedResponse(ResponseModel[PaginatedData[T]], Generic[T]):
    pass
