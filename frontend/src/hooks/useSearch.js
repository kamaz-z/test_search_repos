import { useEffect, useState } from "react";
import { searchGithub } from "../services/searchApi";

const MIN_QUERY_LENGTH = 3;

const INITIAL_STATE = {
  status: "initial",
  items: [],
  totalCount: 0,
  error: null,
};

// Керує пошуком: отримує вже debounced запит і тип сутності
export function useSearch(query, type) {
  const [state, setState] = useState(INITIAL_STATE);

  useEffect(() => {
    const trimmedQuery = query.trim();

    if (trimmedQuery.length < MIN_QUERY_LENGTH) {
      setState(INITIAL_STATE);
      return;
    }

    // Кожен новий запит скасовує попередній, тому застарілі відповіді не потрапляють на екран
    const controller = new AbortController();
    setState((prev) => ({ ...prev, status: "loading", error: null }));

    searchGithub({ type, query: trimmedQuery, signal: controller.signal })
      .then((data) => {
        if (data.items.length === 0) {
          setState({ status: "empty", items: [], totalCount: 0, error: null });
          return;
        }
        setState({
          status: "success",
          items: data.items,
          totalCount: data.total_count,
          error: null,
        });
      })
      .catch((error) => {
        if (error.name === "AbortError") return;
        setState({ status: "error", items: [], totalCount: 0, error: error.message });
      });

    // Функція очищення спрацьовує при зміні query або type і при розмонтуванні компонента
    return () => controller.abort();
  }, [query, type]);

  return state;
}