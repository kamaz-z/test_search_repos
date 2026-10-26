export async function loginAdmin({ username, password }) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Не вдалося увійти");
  }
  return data; // { token, username, is_staff }
}

export async function clearCache(token) {
  const response = await fetch("/api/clear-cache/", {
    method: "POST",
    headers: { Authorization: `Token ${token}` },
  });

  const data = await response.json().catch(() => ({}));
  if (response.status === 401 || response.status === 403) {
    const error = new Error("Немає прав адміністратора");
    error.isAuthError = true;
    throw error;
  }
  if (!response.ok) {
    throw new Error(data.detail || `Помилка запиту (${response.status})`);
  }
  return data.deleted_keys;
}