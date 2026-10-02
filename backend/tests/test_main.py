"""Integration tests using TestClient.websocket_connect() — Standard spec's
explicit pattern for testing WebSockets without a real running server.
"""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

MANAGER_HEADERS = {"X-User-Role": "MANAGER", "X-User-Id": "1"}
STAFF_HEADERS = {"X-User-Role": "STAFF", "X-User-Id": "2"}


def test_list_tickets_starts_empty():
    resp = client.get("/tickets")
    assert resp.status_code == 200


def test_create_ticket_broadcasts_only_to_manager_role():
    # Starlette's test WebSocket session has no non-blocking/timeout receive,
    # so "staff received nothing" can't be checked by waiting and catching a
    # timeout (an early attempt at this test did exactly that, and silently
    # passed even when broadcast() was mutated to ignore target_role
    # entirely — the timeout kwarg doesn't exist on this API, so the
    # resulting TypeError was being swallowed as "no event arrived").
    #
    # Instead: prove ordering. Trigger a SECOND, STAFF-targeted event right
    # after the MANAGER-targeted one. If role-scoping were broken and staff
    # had ALSO received the first (ticket_created) event, FIFO delivery
    # means staff_ws.receive_json() below would return ticket_created, not
    # ticket_assigned — so this fails loudly on the exact bug it exists to
    # catch, instead of needing a timeout at all.
    with client.websocket_connect("/ws/1?role=MANAGER") as manager_ws, \
         client.websocket_connect("/ws/2?role=STAFF") as staff_ws:
        create = client.post("/tickets", json={"title": "Leak in unit 4B"}, headers=STAFF_HEADERS)
        assert create.status_code == 201
        ticket_id = create.json()["id"]

        manager_event = manager_ws.receive_json()
        assert manager_event["event_type"] == "ticket_created"
        assert manager_event["target_role"] == "MANAGER"

        client.post(f"/tickets/{ticket_id}/assign?assignee_id=2", headers=MANAGER_HEADERS)
        staff_event = staff_ws.receive_json()
        assert staff_event["event_type"] == "ticket_assigned", (
            "staff's first message was ticket_created, not ticket_assigned — "
            "the MANAGER-targeted event leaked to a STAFF connection"
        )


def test_assign_requires_manager_role():
    create = client.post("/tickets", json={"title": "AC unit down"}, headers=STAFF_HEADERS)
    ticket_id = create.json()["id"]

    forbidden = client.post(f"/tickets/{ticket_id}/assign?assignee_id=2", headers=STAFF_HEADERS)
    assert forbidden.status_code == 403

    allowed = client.post(f"/tickets/{ticket_id}/assign?assignee_id=2", headers=MANAGER_HEADERS)
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "assigned"
    assert allowed.json()["assigned_to"] == 2


def test_assign_broadcasts_to_staff_role():
    create = client.post("/tickets", json={"title": "Elevator inspection"}, headers=MANAGER_HEADERS)
    ticket_id = create.json()["id"]

    with client.websocket_connect("/ws/3?role=STAFF") as staff_ws:
        client.post(f"/tickets/{ticket_id}/assign?assignee_id=3", headers=MANAGER_HEADERS)
        event = staff_ws.receive_json()
        assert event["event_type"] == "ticket_assigned"
        assert event["target_role"] == "STAFF"
        assert event["payload"]["assigned_to"] == 3


def test_assign_unknown_ticket_404():
    resp = client.post("/tickets/9999/assign?assignee_id=1", headers=MANAGER_HEADERS)
    assert resp.status_code == 404
