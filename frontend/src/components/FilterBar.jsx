export default function FilterBar({ filters, onChange }) {
  return (
    <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
      {filters.map(f => (
        <select
          key={f.name}
          value={f.value}
          onChange={e => onChange(f.name, e.target.value)}
        >
          <option value="">All {f.label}</option>
          {f.options.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      ))}
    </div>
  );
}
