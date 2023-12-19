from typing import Dict, Optional
from pydantic import BaseModel


class ProcessFileRequest(BaseModel):
    body_content: str
    metadata: Optional[Dict[str, str]]