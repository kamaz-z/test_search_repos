import { useState } from "react";

const STORAGE_KEY = "adminSession";

function readSession() {
  try {
    return JSON.parse(sessionStorage.getItem(STORAGE_KEY)) || null;
  } catch {
    return null;
  }
}

// Зберігає токен і прапорець is_staff. Сесія живе, поки відкрита вкладка.
export function useAdminSession() {
  const [session, setSession] = useState(readSession);

  function saveSession(data) {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    setSession(data);
  }

  function clearSession() {
    sessionStorage.removeItem(STORAGE_KEY);
    setSession(null);
  }

  return {
    token: session?.token ?? null,
    username: session?.username ?? null,
    isStaff: Boolean(session?.is_staff),
    saveSession,
    clearSession,
  };
}