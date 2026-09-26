"""Email Ingestion & Parsing Schemas

Defines Pydantic representations for raw inputs and parsed static email artifacts.
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class EmailAnalysisInput(BaseModel):
    raw_email: str = Field(..., description="Raw RFC-822 email text, header dump, or plain text")
    file_name: Optional[str] = Field(default=None, description="Optional uploaded file name")


class AttachmentMetadata(BaseModel):
    filename: str
    extension: str
    double_extension: bool = False
    mime_type: str
    size_bytes: int
    sha256: str
    is_executable: bool = False
    is_macro_enabled: bool = False


class HeaderInfo(BaseModel):
    from_header: str = ""
    sender_name: str = ""
    sender_email: str = ""
    sender_domain: str = ""
    to_header: str = ""
    subject: str = ""
    date: str = ""
    reply_to: Optional[str] = None
    reply_to_domain: Optional[str] = None
    return_path: Optional[str] = None
    return_path_domain: Optional[str] = None
    message_id: Optional[str] = None
    authentication_results: Optional[str] = None
    received_spf: Optional[str] = None
    raw_headers: Dict[str, str] = Field(default_factory=dict)


class ParsedEmail(BaseModel):
    headers: HeaderInfo
    body_plain: str = ""
    body_html: str = ""
    urls: List[str] = Field(default_factory=list)
    attachments: List[AttachmentMetadata] = Field(default_factory=list)
    sha256: str = ""
