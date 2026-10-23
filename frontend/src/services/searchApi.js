export async function searchGithub({ type, query, signal }) {
  const response = await fetch("/api/search/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ type, query }),
    signal,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`);
  }

  return data;
}
