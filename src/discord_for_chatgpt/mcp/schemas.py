from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    method: str
    params: dict = Field(default_factory=dict)
