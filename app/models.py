from pydantic import BaseModel

class SherlockResult(BaseModel):
    site: str
    url: str
    
class JohnCrackRequest(BaseModel):
    password: str

class JohnCrackResult(BaseModel):
    speed: float               # guesses per second
    keyspace: int              # total possibilities
    est_time: str              # human‐readable
    feedback: str              # fun message
