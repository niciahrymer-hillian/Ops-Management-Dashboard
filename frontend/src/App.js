import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// Deliberately minimal: this lesson's depth is the WebSocket/RBAC pattern,
// not dashboard UI polish. A real build would add filtering, role-specific
// views, and the manager-only assign action this README promises.
import { useTickets } from "./hooks/useTickets";
export function App() {
    const { data: tickets, isLoading } = useTickets();
    if (isLoading)
        return _jsx("p", { children: "Loading tickets\u2026" });
    return (_jsxs("div", { children: [_jsx("h1", { children: "Ops Dashboard" }), _jsx("p", { children: "Live-updating via WebSocketProvider \u2014 no polling, no manual refresh." }), _jsx("ul", { children: tickets?.map((t) => (_jsxs("li", { children: [t.title, " \u2014 ", _jsx("b", { children: t.status }), t.assigned_to != null && ` (assigned to #${t.assigned_to})`] }, t.id))) })] }));
}
