import RepositoryCard from "./RepositoryCard";
import UserCard from "./UserCard";

export default function ResultsGrid({ type, items }) {
  return (
    <ul className="results-grid">
      {items.map((item) => (
        <li key={item.id}>
          {type === "users" ? <UserCard user={item} /> : type === "issues" ? <IssueCard issue={item} /> : <RepositoryCard repo={item} />}
        </li>
      ))}
    </ul>
  );
}