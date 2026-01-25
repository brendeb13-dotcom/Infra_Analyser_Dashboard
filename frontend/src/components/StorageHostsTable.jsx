export default function StorageHostsTable({ hosts, onSelect }) {
  return (
    <table border="1" cellPadding="10" width="100%">
      <thead>
        <tr>
          <th>Host</th>
          <th>IP</th>
          <th>HBAs</th>
          <th>LUNs</th>
          <th>Last Seen</th>
        </tr>
      </thead>
      <tbody>
        {hosts.map(h => (
          <tr key={h.hostname} onClick={() => onSelect(h)}>
            <td>{h.hostname}</td>
            <td>{h.ip}</td>
            <td>{h.hbas.length}</td>
            <td>{h.luns.length}</td>
            <td>{new Date(h.last_seen).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
