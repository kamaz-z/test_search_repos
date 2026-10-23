const API_URL = "/api/search";

// Робить запит до бекенду і повертає готові дані або кидає помилку з текстом для користувача
export async function searchGithub({ type, query, signal }) {
  let response;
  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, query }),
      signal,
    });
  } catch (error) {
    // Скасування запиту не є помилкою з'єднання, пробрасуємо його далі
    if (error.name === "AbortError") throw error;
    throw new Error("Немає зв'язку з сервером");
  }

  // Якщо тіло не є JSON, використовуємо порожній об'єкт
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    // Бекенд повертає поле detail для 429, 502, 504 та 403
    throw new Error(data.detail || `Помилка запиту (${response.status})`);
  }

  return data;
}