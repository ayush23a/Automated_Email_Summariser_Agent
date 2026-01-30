from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class EmailItem(BaseModel):
    id: str
    subject: str
    sender: str
    body: str
    received_at: str

class EmailSummary(BaseModel):
    id: str
    subject: str = Field(description="Subject of the email")
    sender: str = Field(description="Sender of the email")
    summary_points: List[str] = Field(description="Key points of the email")
    category: Literal["Marketing", "Job Updates", "Careers", "Finance", "Social", "System", "Other"] = Field(
        description="Category of the email"
    )
    importance: int = Field(description="Importance score from 1 to 5")

    @field_validator("importance", mode="before")
    @classmethod
    def coerce_importance(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

class GraphState(BaseModel):
    raw_emails: List[EmailItem] = []
    analyzed_emails: List[EmailSummary] = []
    final_digest: str = ""
    error: Optional[str] = None
