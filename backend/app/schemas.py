from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

Role = Literal["STAFF", "MANAGER"]


class WSEvent(BaseModel):
    """The one shape every WebSocket message takes, in either direction of
    this lesson: event_type names what happened, payload carries the data,
    actor_id says who caused it, and target_role is how ConnectionManager
    decides who receives it ("ALL" for everyone, or a specific role).
    """

    event_type: str
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: int
    target_role: str = "ALL"


class TicketCreate(BaseModel):
    title: str


class Ticket(BaseModel):
    id: int
    title: str
    status: Literal["open", "assigned", "resolved"] = "open"
    assigned_to: int | None = None
    created_by: int
