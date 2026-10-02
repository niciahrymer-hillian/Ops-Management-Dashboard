// A WebSocket connection that survives the backend restarting, a laptop
// sleeping, or a flaky network — none of which should force a page reload
// to get live updates working again.
import { useEffect, useRef } from "react";
export function useWebSocket(url, onEvent) {
    // onEvent is captured in a ref so a parent re-render (which creates a new
    // function identity every time) doesn't force the effect below to tear
    // down and reopen the socket — only `url` changing should do that.
    const onEventRef = useRef(onEvent);
    onEventRef.current = onEvent;
    useEffect(() => {
        let socket;
        let reconnectTimer;
        let closedByEffectCleanup = false;
        function connect() {
            socket = new WebSocket(url);
            socket.onmessage = (raw) => {
                const event = JSON.parse(raw.data);
                onEventRef.current(event);
            };
            socket.onclose = () => {
                // The trap: without this guard, unmounting the component (which
                // closes the socket deliberately) would ALSO trigger a reconnect —
                // a component that's gone would keep resurrecting its own
                // connection forever.
                if (!closedByEffectCleanup) {
                    reconnectTimer = setTimeout(connect, 2000);
                }
            };
        }
        connect();
        return () => {
            closedByEffectCleanup = true;
            clearTimeout(reconnectTimer);
            socket.close();
        };
    }, [url]);
}
