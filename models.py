from pydantic import BaseModel
from typing import Optional

class FrameParserRequest(BaseModel):
    implementation: str

class StartAnalysisRequest(BaseModel):
    rtmp_url: str

class StopAnalysisRequest(BaseModel):
    rtmp_url: str

class APIResponse(BaseModel):
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    details: Optional[str] = None