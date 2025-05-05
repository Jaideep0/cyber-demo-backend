from pydantic import BaseModel

class SherlockResult(BaseModel):
    site: str
    url: str
