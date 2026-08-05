# 📟 Ops-Management-Dashboard
### Real-time ops dashboard — WebSockets, RBAC, live UI updates.

![Chain C](https://img.shields.io/badge/Chain%20C-Project%203-378ADD?style=for-the-badge) [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue?style=for-the-badge)](LICENSE-GPL) [![License: AGPL v3](https://img.shields.io/badge/License-AGPLv3-blue?style=for-the-badge)](LICENSE-AGPL)

[📖 Lesson Plan](docs/LESSON_PLAN.md) · [🚀 Live Demo](#)

<!-- SCREENSHOT PLACEHOLDER: docs/screenshots/overview.png -->

## Why This Was Built

Internal tools decide whether an operations team's day is calm or chaotic, and they're usually the least
cared-for software in a company. I've been on the operations side of that trade, refreshing a page to find
out whether something had happened yet.

This is the version I'd have wanted: live updates pushed to the browser instead of polling, role-based
access so people see what's theirs, and a layout built around the handful of things someone actually needs
to know at a glance.

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI WebSockets | — | Push live updates to connected dashboards |
| React | — | Dashboard UI with live-updating panels |
| RBAC | — | Role-based access so each user sees only their scope |
| React Query | — | Client-side cache and refetching for dashboard data |

## Project Structure

```
Ops-Management-Dashboard/
├── README.md
├── docs/{LESSON_PLAN.md, interactive/index.html, screenshots/}
├── LICENSE-GPL
└── LICENSE-AGPL
```

## Getting Started

```bash
git clone https://github.com/niciahrymer-hillian/Ops-Management-Dashboard.git
cd Ops-Management-Dashboard
# Backend
uvicorn app.main:app --reload

# Frontend
npm install && npm run dev

# Open the dashboard and watch a second browser update live
open http://localhost:5173
```

## Chain Navigation

Part of **Chain C — Full-Stack + Infrastructure** in the [Post-Bootcamp-Challenge](https://github.com/niciahrymer-hillian/Post-Bootcamp-Challenge) portfolio.

---

Dual licensed — [GPL v3](LICENSE-GPL) and [AGPL v3](LICENSE-AGPL).
