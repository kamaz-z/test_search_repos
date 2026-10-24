import RepositoryCard from "./RepositoryCard";
import UserCard from "./UserCard";

export default function ResultsGrid({ type, items }) {
  return (
    <ul className="results-grid">
      {items.map((item) => (
        <li key={item.id}>
          {type === "users" ? <UserCard user={item} />  : type === "repositories" ? <RepositoryCard repo={item} /> : null}
        </li>
      ))}
    </ul>
  );
}