const TYPE_LABELS = { repositories: "Repository", users: "User" };

export default function SearchHistory({ items, onSelect }) {
  // Issues у фронтенді не підтримуємо, тому такі записи ховаємо
  const visibleItems = items.filter((item) => TYPE_LABELS[item.type]);

  if (visibleItems.length === 0) return null;

  return (
    <section className="history">
      <h2 className="history__title">Останні запити</h2>
      <ul className="history__list">
        {visibleItems.map((item) => (
          <li key={`${item.type}:${item.query}`}>
            <button
              className="history__item"
              onClick={() => onSelect(item)}
            >
              {item.query}
              <span className="history__type">{TYPE_LABELS[item.type]}</span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
