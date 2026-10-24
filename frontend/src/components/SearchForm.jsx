export default function SearchForm({ query, onQueryChange, type, onTypeChange }) {
  return (
    <form className="search-form" onSubmit={(event) => event.preventDefault()}>
      <input
        className="search-input"
        type="text"
        placeholder="Введіть щонайменше 3 символи"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
      />
      <select
        className="search-select"
        value={type}
        onChange={(event) => onTypeChange(event.target.value)}
      >
        <option value="repositories">Repository</option>
        <option value="users">User</option>
      </select>
    </form>
  );
}