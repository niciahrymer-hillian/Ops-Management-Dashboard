"""Ops-Management-Dashboard — trimmed to the WebSocket + RBAC pattern this
lesson teaches. No database (in-memory tickets), same reasoning as C-2: the
point is the broadcast/connection/authorization pattern, not re-teaching
persistence.
"""
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status

from app.connection_manager import manager
from app.deps import get_current_role, get_current_user_id, require_manager
from app.schemas import Role, Ticket, TicketCreate, WSEvent

app = FastAPI(title="Ops-Management-Dashboard API")

TICKETS: dict[int, Ticket] = {}
_next_id = 1


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, role: Role) -> None:
    await manager.connect(user_id, role, websocket)
    try:
        while True:
            # This dashboard only receives broadcasts — it doesn't need to
            # send anything — but the loop still has to await a message (or
            # the disconnect) to know when the client actually went away.
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(user_id)


@app.get("/tickets")
def list_tickets() -> list[Ticket]:
    return list(TICKETS.values())


@app.post("/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    payload: TicketCreate,
    role: Role = Depends(get_current_role),
    user_id: int = Depends(get_current_user_id),
) -> Ticket:
    global _next_id
    ticket = Ticket(id=_next_id, title=payload.title, created_by=user_id)
    TICKETS[ticket.id] = ticket
    _next_id += 1

    # REST call -> update "DB" (the dict above) -> broadcast. Managers need
    # to see new tickets as they arrive; staff don't need every creation
    # pushed at them, so target_role scopes the broadcast instead of a
    # blanket "ALL".
    await manager.broadcast(WSEvent(
        event_type="ticket_created",
        payload=ticket.model_dump(mode="json"),
        actor_id=ticket.created_by,
        target_role="MANAGER",
    ))
    return ticket


@app.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: int,
    assignee_id: int,
    role: Role = Depends(require_manager),
    manager_id: int = Depends(get_current_user_id),
) -> Ticket:
    ticket = TICKETS.get(ticket_id)
    if ticket is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such ticket")
    ticket.status = "assigned"
    ticket.assigned_to = assignee_id
    TICKETS[ticket_id] = ticket

    # The reverse scoping from create_ticket: assignment matters to staff
    # (someone just got handed work), not to every other manager. actor_id
    # is the MANAGER who assigned it, not the assignee — the event says who
    # did the thing, payload says who it was done to.
    await manager.broadcast(WSEvent(
        event_type="ticket_assigned",
        payload=ticket.model_dump(mode="json"),
        actor_id=manager_id,
        target_role="STAFF",
    ))
    return ticket
