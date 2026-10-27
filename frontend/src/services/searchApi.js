
const API_URL = "/api/search/";

export async function searchGithub({ type, query, page = 1, signal }) {
  let response;

  const token = sessionStorage.getItem("authToken");

  try {
    response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Token ${token}` } : {}),
      },
      body: JSON.stringify({ type, query, page }),
      signal,
    });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error("Немає зв'язку з сервером");
  }

  const data = await response.json().catch(() => ({}));

  if (response.status === 401 || response.status === 403) {
    if (response.status === 401) {
      sessionStorage.removeItem("authToken");
      window.dispatchEvent(new Event("auth-required"));
      throw new Error("Сесія завершилася. Увійдіть знову.");
    }
  }

  if (!response.ok) {
    throw new Error(data.detail || `Помилка запиту (${response.status})`);
  }

  return data;
}
