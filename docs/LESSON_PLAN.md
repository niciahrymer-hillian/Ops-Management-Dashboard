# 📖 Lesson Plan — Ops-Management-Dashboard

| Field | Value |
|-------|-------|
| Chain | Chain C — Full-Stack + Infrastructure (project C-3 of 4) |
| Difficulty | Intermediate–Advanced |
| Estimated time | ~3 weeks |
| Prerequisite | [Full-Stack-Job-Board](../../Full-Stack-Job-Board) (C-1) |
| Next project | [Kubernetes-IaC-Deployment](../../Kubernetes-IaC-Deployment) (C-4) |
| Primary license | AGPL v3 (deployed web app) |
| From scratch | No — skeleton scaffold (working bones + TODOs) |

## What This Project Is

Everything so far has been request/response: ask, wait, get an answer. This
project is the other shape — the server pushes to the browser the moment
something happens, with no request involved. A `ConnectionManager` tracks
every connected dashboard by `user_id` and role; a REST call that changes
data (creating or assigning a ticket) broadcasts an event to exactly the
connections whose role should see it, and the frontend turns that push into
a React Query cache invalidation instead of a poll loop.

Trimmed from a real app the same way C-2 was: no database, in-memory
tickets, no real login (role/user id come from headers/query params) — the
depth here is the WebSocket + RBAC pattern, not re-teaching persistence or
JWT auth that C-1 already covers.

## Learning Objectives

- Explain what a WebSocket connection has that a sequence of HTTP requests
  doesn't, and why that matters for "push, not poll."
- Build a `ConnectionManager` that can target a broadcast to a subset of
  connections (by role), not just "everyone currently connected."
- Write a FastAPI dependency *factory* (`require_manager`) that enforces
  authorization independently of how authentication happened.
- Write an integration test for a WebSocket endpoint using
  `TestClient.websocket_connect()` — and recognize when such a test is
  passing for the wrong reason.
- Build a reconnecting WebSocket client in React without creating a
  resurrection loop when the component unmounts.
- Explain why "an event arrived" should usually mean "invalidate a query,"
  not "manually patch this one piece of state."

## Software You Will Use

| Tool | What it is | Why it matters here | Install | Docs |
|------|-----------|----------------------|---------|------|
| FastAPI WebSockets | `@app.websocket(...)`, `WebSocketDisconnect` | The server-push half of this project | bundled with FastAPI | [FastAPI — WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) |
| FastAPI TestClient | `websocket_connect()` | Integration-tests a WebSocket endpoint without a real running server | bundled with FastAPI | [FastAPI — Testing WebSockets](https://fastapi.tiangolo.com/advanced/testing-websockets/) |
| `websockets` (Python) | Standalone async WS client | Used for the live, real-server smoke test (not just TestClient) | `pip install websockets` | — |
| Browser WebSocket API | `new WebSocket(url)`, `.onmessage`, `.onclose` | What `useWebSocket.ts` wraps | built into every browser | [MDN — WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) |
| TanStack Query v5 | `invalidateQueries` | How a pushed event becomes a UI update | `npm install @tanstack/react-query` | [TanStack Query — Invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation) |

## The Event Protocol

Every message, in either direction of this lesson, is one shape:

```json
{"event_type": "ticket_created", "payload": {...}, "timestamp": "...",
 "actor_id": 2, "target_role": "MANAGER"}
```

`target_role` is what `ConnectionManager.broadcast()` reads to decide who
receives it — `"MANAGER"`, `"STAFF"`, or `"ALL"`.

## Build Order

- **Week 1 — WebSocket endpoint + ConnectionManager.** `connection_manager.py`'s
  `active_connections: dict[int, tuple[WebSocket, str]]`, `connect()`,
  `disconnect()`, `broadcast()`. The `/ws/{user_id}` endpoint, accepting a
  `role` query param. *Verify: two separate WebSocket connections, a manual
  `broadcast()` call, confirm only the matching-role connection receives it
  — see Lesson 2's note on a test that LOOKED like it verified this and didn't.*
- **Week 1.5 — RBAC.** `deps.py`'s `get_current_role` / `require_manager`.
  Gate `POST /tickets/{id}/assign` behind `require_manager`.
  *Verify: the same request with `X-User-Role: STAFF` → 403; `MANAGER` → 200.*
- **Week 2 — Wire REST to WebSocket.** `POST /tickets` broadcasts
  `ticket_created` to `MANAGER`; `POST /tickets/{id}/assign` broadcasts
  `ticket_assigned` to `STAFF`. *Verify: run a real `uvicorn` server, open two
  real `websockets` client connections from a script, confirm each receives
  only its own event — not just the in-process TestClient version.*
- **Week 2.5 — Frontend.** `useWebSocket.ts` (connect, reconnect on close,
  guard against reconnecting after a deliberate unmount),
  `WebSocketProvider.tsx` (invalidate `["tickets"]` on any `ticket_*` event).
  *Verify: `npx tsc --noEmit` is clean, `npm run build` succeeds.*

## Common Mistakes to Avoid

- **A WebSocket test that can't fail.** An early version of this project's
  own test asserted "the staff socket received nothing" by calling
  `receive_json(timeout=0.2)` inside a try/except. Starlette's test session
  doesn't accept a `timeout` kwarg at all — so every call raised `TypeError`
  immediately, the broad `except Exception` caught it, and the test reported
  "staff received nothing" whether or not that was true. Mutating
  `broadcast()` to ignore `target_role` entirely still passed. The fix:
  prove *ordering* (trigger a second, differently-targeted event and assert
  which one arrives first) instead of trying to prove *absence* with a
  timeout the test client doesn't support.
- **Reconnecting after you meant to disconnect.** `ws.onclose` firing on a
  deliberate `socket.close()` (component unmount) looks identical to the
  connection actually dropping — without a guard flag, every unmount starts
  an immortal reconnect loop for a component that no longer exists.
- **A `switch` on `event_type` in the frontend.** Matching each event type to
  a specific cache-patching action means the frontend has to be updated
  every time the backend adds an event type. Invalidating by a shared prefix
  (`ticket_*` → invalidate `["tickets"]`) means new event types just work.
- **Authorizing in the route body instead of a dependency.** `require_manager`
  as a dependency means FastAPI returns `403` before the route function body
  — including `TICKETS.get(...)` — ever runs. An `if role != "MANAGER"` check
  written inline, after other logic, is one refactor away from being
  skipped.

## Why This Matters (Industry Application)

**What this skill is used for in the real world**
Any product with more than one person watching the same data live — ops
dashboards, trading tools, chat, delivery tracking, collaborative editors —
needs this exact pattern: a connection registry, scoped broadcasting, and a
client that turns a push into a cache update instead of a full refetch.

**Roles that hire for it**
- Full-Stack Engineer · Backend Engineer (real-time systems)
- Platform Engineer building internal tools

**Why it strengthens *my* portfolio**
This is the same pattern Centric's after-hours agent and Keyholders'
field-ops dashboards need for live status updates — built here first, on a
small trimmed app, with the RBAC half directly reusable for any
operator/resident/technician-scoped view.

**How it connects to the rest of the portfolio**
- Builds on: [C-1 — Full-Stack-Job-Board](../../Full-Stack-Job-Board), [C-2 — Dockerized-Microservices](../../Dockerized-Microservices)
- Feeds into: [C-4 — Kubernetes-IaC-Deployment](../../Kubernetes-IaC-Deployment)

## Reflection Questions

1. What can a WebSocket connection do that a client polling `GET /tickets` every 2 seconds cannot?
2. Why does `ConnectionManager` store `(websocket, role)` tuples keyed by `user_id`, rather than just a list of sockets?
3. The project's own first WebSocket test passed even when broadcast scoping was completely broken. What made that possible, and what does the fixed version prove instead?
4. Why does `require_manager` live as a FastAPI dependency rather than an `if` statement inside the route function?
5. In `useWebSocket.ts`, what specific bug does `closedByEffectCleanup` prevent, and under what circumstance would you see it without that guard?
6. Why does `WebSocketProvider` invalidate a query key instead of directly calling `setQueryData` with the pushed payload?

## Topics to Research

- [FastAPI — WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI — Testing WebSockets](https://fastapi.tiangolo.com/advanced/testing-websockets/)
- [MDN — WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [TanStack Query — Query Invalidation](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation)

## How This Connects Forward

**C-4** deploys this alongside C-1/C-2 on Kubernetes — a WebSocket connection
has a real consequence there that HTTP doesn't: a long-lived connection
means a load balancer needs **session affinity** (or a shared pub/sub layer
like Redis) once there's more than one replica, since a broadcast triggered
on replica A does nothing for a client connected to replica B.

## Git Commit Checklist

- [ ] Conventional commits, one feature each (`feat:`, `fix:`, `chore:`).
- [ ] Backend and frontend changes in separate commits.
- [ ] Never commit `.env`, `node_modules/`, or `dist/`.
