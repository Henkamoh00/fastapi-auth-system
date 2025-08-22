from typing import Optional
from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str