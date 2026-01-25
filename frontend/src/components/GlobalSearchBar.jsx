export default function GlobalSearchBar({ value, onChange }) {
  return (
    <input
      type="text"
      placeholder="Search across dashboard…"
      value={value}
      onChange={e => onChange(e.target.value)}
      style={{
        width: "100%",
        padding: "10px",
        fontSize: "1rem",
        marginBottom: "16px",
        borderRadius: "6px",
        border: "1px solid #ccc"
      }}
    />
  );
}
