
import { useState } from "react";
import { loginUser } from "../services/authApi";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await loginUser({ username, password });

      if (!data.token) {
        throw new Error("Сервер не повернув токен");
      }

      sessionStorage.setItem("authToken", data.token);
      sessionStorage.setItem("authSession", JSON.stringify(data));
      onLogin(data);
    } catch (err) {
      setError(err.message || "Не вдалося увійти");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-container">
      <form className="login-form" onSubmit={handleSubmit}>
        <h1>Вхід</h1>

        <label htmlFor="username">Username</label>
        <input
          id="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          autoComplete="username"
          required
        />

        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />

        {error && <p role="alert">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Вхід..." : "Увійти"}
        </button>
      </form>
    </main>
  );
}
