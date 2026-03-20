export default function StorageHostsTable({ hosts, onSelect }) {
  return (
    <table border="1" cellPadding="10" width="100%">
      <thead>
        <tr>
          <th>Host</th>
          <th>IP</th>
          <th>OS</th>
          <th>HBAs</th>
          <th>LUNs</th>

          {/* 🔥 NEW */}
          <th>Capacity (GB)</th>
          <th>Vendors</th>
          <th>Drivers</th>

          <th>Last Seen</th>
        </tr>
      </thead>

      <tbody>
        {hosts.map(h => (
          <tr
            key={h.hostname}
            onClick={() => onSelect(h)}
            style={{ cursor: "pointer" }}
          >
            <td>{h.hostname}</td>
            <td>{h.ip}</td>
            <td>{h.os}</td>

            <td>{h.hbas.length}</td>
            <td>{h.luns.length}</td>

            {/* 🔥 NEW */}
            <td>{h.total_capacity_gb || 0}</td>

            <td>
              {h.lun_vendors?.length > 0
                ? h.lun_vendors.join(", ")
                : "—"}
            </td>

            <td>
              {h.hba_drivers?.length > 0
                ? h.hba_drivers.join(", ")
                : "—"}
            </td>

            <td>{new Date(h.last_seen).toLocaleString()}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}