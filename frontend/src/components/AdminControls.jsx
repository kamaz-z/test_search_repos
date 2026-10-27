import { useState } from "react";
import { clearCache } from "../services/adminApi";

export default function AdminControls({ token, username, isStaff, onLogout }) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  if (!isStaff) return null;

  async function handleClearCache() {
    setIsBusy(true);
    setError("");
    setMessage("");
    try {
      const deleted = await clearCache(token);
      setMessage(`Кеш очищено, видалено ключів: ${deleted}`);
    } catch (err) {
      setError(err.message);
      if (err.isAuthError) onLogout();
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <div className="admin-controls">
      <p className="admin-controls__user">Адмін: {username}</p>
      <div className="admin-controls__actions">
        <button className="load-more" onClick={handleClearCache} disabled={isBusy}>
          {isBusy ? "Очищення..." : "Очистити кеш"}
        </button>
        <button className="load-more" onClick={onLogout} disabled={isBusy}>
          Вийти
        </button>
      </div>
      {message && <p className="status">{message}</p>}
      {error && <p className="status status--error">{error}</p>}
    </div>
  );
}
