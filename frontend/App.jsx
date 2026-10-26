import { useState,useEffect } from "react";
import ResultsGrid from "./src/components/ResultsGrid.jsx";
import SearchForm from "./src/components/SearchForm.jsx";
import StatusMessage from "./src/components/StatusMessage.jsx";
import { useDebounce } from "./src/hooks/useDebounce.js";
import { useSearch } from "./src/hooks/useSearch.js";
import AdminControls from "./src/components/AdminControls.jsx";
import SearchHistory from "./src/components/SearchHistory";
import { useSearchHistory } from "./src/hooks/useSearchHistory";



export default function App() {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("repositories");
  const debouncedQuery = useDebounce(query, 400);
  const { status, items, totalCount, error,hasMore,isLoadingMore,loadMore } = useSearch(debouncedQuery, type);
  const { history, reload: reloadHistory } = useSearchHistory();

// Після успішного пошуку бекенд міг додати запит в історію
useEffect(() => {
  if (status === "success") reloadHistory();
}, [status, debouncedQuery, type, reloadHistory]);

function handleSelectHistory(item) {
  setQuery(item.query);
  setType(item.type);
}

  return (
    <main className="app">
      <header className="app__header">
        <p className="app__eyebrow">OPEN SOURCE INDEX</p>
        <h1 className="app__title">GitHub Search</h1>
        <p className="app__intro">
          Explore repositories and developers across GitHub.
        </p>
      </header>

      <SearchForm
        query={query}
        onQueryChange={setQuery}
        type={type}
        onTypeChange={setType}
      />
      <SearchHistory items={history} onSelect={handleSelectHistory} />

      {status === "success" && (
        <p className="app__total">{totalCount.toLocaleString()} results</p>
      )}

      <section className="app__results" aria-live="polite">
        <StatusMessage status={status} error={error} />
        {status === "success" && (
  <>
    <ResultsGrid items={items} type={type} />

    {hasMore && (
      <button
        className="load-more"
        onClick={loadMore}
        disabled={isLoadingMore}
      >
        {isLoadingMore ? "Завантаження..." : "Показати ще"}
      </button>
    )}
  </>
)}      </section>
<AdminControls />

    </main>
  );
}
