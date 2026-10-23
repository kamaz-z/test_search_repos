export default function UserCard({ user }) {
  return (
    <article className="card">
      <img className="card__avatar" src={user.avatar_url} alt={user.login} />
      <h2 className="card__title">{user.login}</h2>
      <a className="card__link" href={user.html_url} target="_blank" rel="noreferrer">
        Відкрити на GitHub
      </a>
    </article>
  );
}