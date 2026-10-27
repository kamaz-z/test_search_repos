import { useCallback, useEffect, useState } from "react";
import { getSearchHistory } from "../services/historyApi";

export function useSearchHistory(enabled = true) {
  const [history, setHistory] = useState([]);

  const reload = useCallback(async () => {
    if (!enabled) {
      setHistory([]);
      return;
    }

    try {
      setHistory(await getSearchHistory());
    } catch (error) {
      console.error("Не вдалося завантажити історію пошуку:", error);
    }
  }, [enabled]);

  // Перше завантаження при відкритті сторінки
  useEffect(() => {
    reload();
  }, [reload]);

  return { history, reload };
}