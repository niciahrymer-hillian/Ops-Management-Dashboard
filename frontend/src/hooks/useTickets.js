import { useQuery } from "@tanstack/react-query";
export function useTickets() {
    return useQuery({
        queryKey: ["tickets"],
        queryFn: async () => {
            const res = await fetch("http://localhost:8000/tickets");
            return (await res.json());
        },
    });
}
