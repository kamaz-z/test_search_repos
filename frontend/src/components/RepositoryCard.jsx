export default function RepositoryCard({ repo }) {
  return (
    <article className="card">
      <h2 className="card__title">{repo.name}</h2>
      <p className="card__meta">Автор: {repo.owner_login}</p>
      <p className="card__description">{repo.description || "Без опису"}</p>
      <div className="card__stats">
        <span>★ {repo.stars.toLocaleString("uk-UA")}</span>
        <span>⑂ {repo.forks.toLocaleString("uk-UA")}</span>
        <span>{repo.language || "Мова не вказана"}</span>
      </div>
      <a className="card__link" href={repo.html_url} target="_blank" rel="noreferrer">
        Відкрити на GitHub
      </a>
    </article>
  );
}