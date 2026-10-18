from pydantic import BaseModel

class SearchInput(BaseModel):
    query: str
    offset: int = 0
