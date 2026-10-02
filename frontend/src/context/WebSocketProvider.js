import { jsx as _jsx } from "react/jsx-runtime";
// Bridges the WebSocket event stream into React Query's cache: a dashboard
// component never touches the socket directly, it just calls useQuery for
// ["tickets"] and this provider is what keeps that query fresh.
import { useQueryClient } from "@tanstack/react-query";
import { createContext } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
const WebSocketContext = createContext(null);
export function WebSocketProvider({ userId, role, children }) {
    const queryClient = useQueryClient();
    const url = `ws://localhost:8000/ws/${userId}?role=${role}`;
    useWebSocket(url, (event) => {
        // Every event type this backend sends is, one way or another, "the
        // tickets list changed" — so invalidating one query key covers
        // ticket_created AND ticket_assigned without a switch statement that
        // has to be kept in sync with the backend's event_type values by hand.
        if (event.event_type.startsWith("ticket_")) {
            queryClient.invalidateQueries({ queryKey: ["tickets"] });
        }
    });
    return (_jsx(WebSocketContext.Provider, { value: null, children: children }));
}
