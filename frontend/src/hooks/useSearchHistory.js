import { useCallback, useEffect, useState } from "react";
import { getSearchHistory } from "../services/historyApi";

export function useSearchHistory() {
  const [history, setHistory] = useState([]);

  const reload = useCallback(async () => {
    try {
      setHistory(await getSearchHistory());
    } catch (error) {
      console.error("Не вдалося завантажити історію пошуку:", error);
    }
  }, []);

  // Перше завантаження при відкритті сторінки
  useEffect(() => {
    reload();
  }, [reload]);

  return { history, reload };
}