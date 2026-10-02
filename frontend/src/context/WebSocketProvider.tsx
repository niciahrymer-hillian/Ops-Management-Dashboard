// Bridges the WebSocket event stream into React Query's cache: a dashboard
// component never touches the socket directly, it just calls useQuery for
// ["tickets"] and this provider is what keeps that query fresh.
import { useQueryClient } from "@tanstack/react-query";
import { createContext, type ReactNode } from "react";

import { useWebSocket, type WSEvent } from "../hooks/useWebSocket";

const WebSocketContext = createContext<null>(null);

interface Props {
  userId: number;
  role: "STAFF" | "MANAGER";
  children: ReactNode;
}

export function WebSocketProvider({ userId, role, children }: Props) {
  const queryClient = useQueryClient();
  const url = `ws://localhost:8000/ws/${userId}?role=${role}`;

  useWebSocket(url, (event: WSEvent) => {
    // Every event type this backend sends is, one way or another, "the
    // tickets list changed" — so invalidating one query key covers
    // ticket_created AND ticket_assigned without a switch statement that
    // has to be kept in sync with the backend's event_type values by hand.
    if (event.event_type.startsWith("ticket_")) {
      queryClient.invalidateQueries({ queryKey: ["tickets"] });
    }
  });

  return (
    <WebSocketContext.Provider value={null}>
      {children}
    </WebSocketContext.Provider>
  );
}
