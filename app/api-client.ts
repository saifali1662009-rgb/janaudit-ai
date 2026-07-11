export type JanauditSource = {
  title: string;
  url: string;
  publisher: string;
  excerpt: string;
  source_type: "official" | "audit" | "parliament" | "news";
};

export type JanauditReport = {
  subject: string;
  scope: string;
  summary: string;
  key_findings: string[];
  confidence: number;
  limitations: string[];
  sources: JanauditSource[];
  money_trail: { stage: string; statement: string; source_title: string; url: string }[];
  used_mesh: boolean;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function post<T>(path: string, body: object): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "Janaudit could not create this report.");
  return payload as T;
}

export function searchJanaudit(query: string) {
  return post<JanauditReport>("/api/search", { query });
}

export function investigateJanaudit(input: {
  category: string;
  subject: string;
  scope: string;
  state?: string | null;
  sections: string[];
}) {
  return post<JanauditReport>("/api/investigations", input);
}
