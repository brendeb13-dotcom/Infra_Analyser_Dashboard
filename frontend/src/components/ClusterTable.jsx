export default function ClusterTable({ clusters, onSelect }) {
  return (
    <table
      border="1"
      cellPadding="10"
      style={{ width: "100%", marginBottom: "24px" }}
    >
      <thead>
        <tr>
          <th>Cluster Name</th>
          <th>Type</th>
          <th>Nodes</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        {clusters.map((c) => (
          <tr
            key={c.name}
            style={{ cursor: "pointer" }}
            onClick={() => onSelect(c.name)}
          >
            <td>{c.name}</td>
            <td>{c.type}</td>
            <td>{c.nodes}</td>
            <td>{new Date(c.last_seen).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
