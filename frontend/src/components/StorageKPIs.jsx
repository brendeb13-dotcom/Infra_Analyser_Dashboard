export default function StorageKPIs({ summary }) {
  const card = {
    border: "1px solid #ccc",
    borderRadius: "8px",
    padding: "12px 20px",
    minWidth: "140px",
    textAlign: "center",
  };

  return (
    <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
      <div style={card}>
        <h4>Hosts</h4>
        <b>{summary.hosts}</b>
      </div>
      <div style={card}>
        <h4>HBAs</h4>
        <b>{summary.hbas}</b>
      </div>
      <div style={card}>
        <h4>LUNs</h4>
        <b>{summary.luns}</b>
      </div>
      <div style={card}>
        <h4>Mappings</h4>
        <b>{summary.mappings}</b>
      </div>
    </div>
  );
}
