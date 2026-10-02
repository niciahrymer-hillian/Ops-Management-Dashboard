import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";

import { App } from "./App";
import { WebSocketProvider } from "./context/WebSocketProvider";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <WebSocketProvider userId={1} role="MANAGER">
        <App />
      </WebSocketProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
