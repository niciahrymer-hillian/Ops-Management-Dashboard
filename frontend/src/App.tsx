// Deliberately minimal: this lesson's depth is the WebSocket/RBAC pattern,
// not dashboard UI polish. A real build would add filtering, role-specific
// views, and the manager-only assign action this README promises.
import { useTickets } from "./hooks/useTickets";

export function App() {
  const { data: tickets, isLoading } = useTickets();

  if (isLoading) return <p>Loading tickets…</p>;

  return (
    <div>
      <h1>Ops Dashboard</h1>
      <p>Live-updating via WebSocketProvider — no polling, no manual refresh.</p>
      <ul>
        {tickets?.map((t) => (
          <li key={t.id}>
            {t.title} — <b>{t.status}</b>
            {t.assigned_to != null && ` (assigned to #${t.assigned_to})`}
          </li>
        ))}
      </ul>
    </div>
  );
}
