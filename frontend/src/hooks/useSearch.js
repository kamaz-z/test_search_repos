import { useCallback, useEffect, useRef, useState } from "react";
import { searchGithub } from "../services/searchApi";

const MIN_QUERY_LENGTH = 3;

const INITIAL_STATE = {
  status: "initial",
  items: [],
  totalCount: 0,
  page: 0,
  hasMore: false,
  isLoadingMore: false,
  error: null,
};

export function useSearch(query, type) {
  const [state, setState] = useState(INITIAL_STATE);
  // Контролер поточного запиту, щоб скасувати його при зміні пошуку
  const controllerRef = useRef(null);

  // Запит однієї сторінки. Для першої сторінки список замінюємо, для наступних додаємо
  const fetchPage = useCallback(
    async (pageToLoad, signal) => {
      const data = await searchGithub({ type, query, page: pageToLoad, signal });
      return data;
    },
    [type, query]
  );

  // Скидання і завантаження першої сторінки при зміні запиту або типу
  useEffect(() => {
    const trimmedQuery = query.trim();
    controllerRef.current?.abort();

    if (trimmedQuery.length < MIN_QUERY_LENGTH) {
      setState(INITIAL_STATE);
      return;
    }

    const controller = new AbortController();
    controllerRef.current = controller;
    setState({ ...INITIAL_STATE, status: "loading" });

    fetchPage(1, controller.signal)
      .then((data) => {
        if (data.items.length === 0) {
          setState({ ...INITIAL_STATE, status: "empty" });
          return;
        }
        setState({
          status: "success",
          items: data.items,
          totalCount: data.total_count,
          page: data.page,
          hasMore: data.has_more,
          isLoadingMore: false,
          error: null,
        });
      })
      .catch((error) => {
        if (error.name === "AbortError") return;
        setState({ ...INITIAL_STATE, status: "error", error: error.message });
      });

    return () => controller.abort();
  }, [query, type, fetchPage]);

  // Наступна сторінка: додаємо її елементи до вже завантажених
  const loadMore = useCallback(() => {
    if (!state.hasMore || state.isLoadingMore) return;

    const controller = new AbortController();
    controllerRef.current = controller;
    const nextPage = state.page + 1;
    setState((prev) => ({ ...prev, isLoadingMore: true }));

    fetchPage(nextPage, controller.signal)
      .then((data) => {
        setState((prev) => ({
          ...prev,
          items: [...prev.items, ...data.items],
          page: data.page,
          hasMore: data.has_more,
          isLoadingMore: false,
        }));
      })
      .catch((error) => {
        if (error.name === "AbortError") return;
        setState((prev) => ({ ...prev, isLoadingMore: false, error: error.message }));
      });
  }, [state.hasMore, state.isLoadingMore, state.page, fetchPage]);

  return { ...state, loadMore };
}