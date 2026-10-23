const MESSAGES = {
  initial: "Почніть вводити запит, щоб побачити результати",
  loading: "Завантаження...",
  empty: "Нічого не знайдено",
};

export default function StatusMessage({ status, error }) {
  if (status === "error") {
    return <p className="status status--error">{error}</p>;
  }
  if (status === "success") {
    return null;
  }
  return <p className="status">{MESSAGES[status]}</p>;
}