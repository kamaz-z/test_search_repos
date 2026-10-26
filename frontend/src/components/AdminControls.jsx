import { useState } from "react";
import { clearCache, loginAdmin } from "../services/adminApi";
import { useAdminSession } from "../hooks/useAdminSession";

export default function AdminControls() {
  const { token, username, isStaff, saveSession, clearSession } = useAdminSession();
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  async function handleLogin(event) {
    event.preventDefault();
    setIsBusy(true);
    setError("");
    try {
      const data = await loginAdmin({ username: login, password });
      saveSession(data);
      setPassword("");
      setIsFormOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsBusy(false);
    }
  }

  async function handleClearCache() {
    setIsBusy(true);
    setError("");
    setMessage("");
    try {
      const deleted = await clearCache(token);
      setMessage(`Кеш очищено, видалено ключів: ${deleted}`);
    } catch (err) {
      setError(err.message);
      // Якщо токен відхилено, прибираємо сесію
      if (err.isAuthError) clearSession();
    } finally {
      setIsBusy(false);
    }
  }

  // Звичайний користувач бачить лише посилання на вхід
  if (!isStaff) {
    return (
      <div className="admin-controls">
        <button
          className="admin-controls__toggle"
          onClick={() => setIsFormOpen((open) => !open)}
        >
          Вхід для адміна
        </button>
        {isFormOpen && (
          <form className="admin-controls__form" onSubmit={handleLogin}>
            <input
              className="search-input"
              placeholder="Логін"
              value={login}
              onChange={(event) => setLogin(event.target.value)}
              autoComplete="username"
            />
            <input
              className="search-input"
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
            />
            <button className="load-more" type="submit" disabled={isBusy}>
              Увійти
            </button>
            {error && <p className="status status--error">{error}</p>
}
          </form>
        )}
      </div>
    );
  }

  // Staff-користувач бачить кнопку очищення кешу
  return (
    <div className="admin-controls">
      <p className="admin-controls__user">Адмін: {username}</p>
      <div className="admin-controls__actions">
        <button className="load-more" onClick={handleClearCache} disabled={isBusy}>
          {isBusy ? "Очищення..." : "Очистити кеш"}
        </button>
        <button className="load-more" onClick={clearSession} disabled={isBusy}>
          Вийти
        </button>
      </div>
      {message && <p className="status">{message}</p>}
      {error && <p className="status status--error">{error}</p>}
    </div>
  );
}