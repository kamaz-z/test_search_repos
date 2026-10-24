import { useState } from "react";
import ResultsGrid from "./src/components/ResultsGrid.jsx";
import SearchForm from "./src/components/SearchForm.jsx";
import StatusMessage from "./src/components/StatusMessage.jsx";
import { useDebounce } from "./src/hooks/useDebounce.js";
import { useSearch } from "./src/hooks/useSearch.js";


export default function App() {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("repositories");
  const debouncedQuery = useDebounce(query, 400);
  const { status, items, totalCount, error,hasMore,isLoadingMore,loadMore } = useSearch(debouncedQuery, type);

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
    </main>
  );
}
