// src/api/client.js  (CRA用)
const BASE = process.env.REACT_APP_API_BASE || "http://127.0.0.1:8000";

export async function postWebhook(message) {
  const res = await fetch(`${BASE}/webhook/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}
