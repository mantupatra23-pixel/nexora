from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID

class WebhookPayload(BaseModel):
    event_type: str = Field(..., example="stripe.payment_intent.succeeded")
    data: Dict[str, Any] = Field(default_factory=dict)

class GoogleSheetsPayload(BaseModel):
    spreadsheet_id: str
    range_name: str
    values: list
