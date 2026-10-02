import { useQuery } from "@tanstack/react-query";

export interface Ticket {
  id: number;
  title: string;
  status: "open" | "assigned" | "resolved";
  assigned_to: number | null;
  created_by: number;
}

export function useTickets() {
  return useQuery({
    queryKey: ["tickets"],
    queryFn: async () => {
      const res = await fetch("http://localhost:8000/tickets");
      return (await res.json()) as Ticket[];
    },
  });
}
