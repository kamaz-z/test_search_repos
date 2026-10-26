const API_URL = "/api/history/";

export async function getSearchHistory() {
  const response = await fetch(API_URL, {
    method: "GET",
    headers: { "Content-Type": "application/json" },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Помилка запиту (${response.status})`);
  }

  return data.history;
}  