const API_URL = "/api/search/";

// Робить запит до бекенду і повертає готові дані або кидає помилку з текстом для користувача
export async function searchGithub({ type, query, page = 1, signal }) {
  let response;
  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, query, page }),
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error("Немає зв'язку з сервером");
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || `Помилка запиту (${response.status})`);
  }

  return data;
}