export default function GlobalSearchBar({ value, onChange }) {
  return (
    <input
      type="text"
      placeholder="Search across dashboard…"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      style={{
        width: "320px",
        padding: "10px 12px",
        borderRadius: "8px",
        border: "1px solid #CBD5E1",
        marginBottom: "16px",
        fontSize: "0.9rem"
      }}
    />
  );
}
