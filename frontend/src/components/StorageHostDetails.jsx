export default function StorageHostDetails({ host }) {
  if (!host) return null;

  return (
    <div style={{ marginTop: "32px" }}>
      <h3>Host Details: {host.hostname}</h3>

      {/* HBAs */}
      <h4>HBAs</h4>
      <table border="1" cellPadding="8" width="100%">
        <thead>
          <tr>
            <th>HBA ID</th>
            <th>WWN</th>
            <th>State</th>
            <th>Speed</th>
            <th>Driver</th>
          </tr>
        </thead>
        <tbody>
          {host.hbas.map((h, i) => (
            <tr key={i}>
              <td>{h.hba_id}</td>
              <td>{h.wwn || "N/A"}</td>
              <td>{h.state}</td>
              <td>{h.speed}</td>
              <td>{h.driver}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* LUNs */}
      <h4 style={{ marginTop: "24px" }}>LUNs</h4>
      <table border="1" cellPadding="8" width="100%">
        <thead>
          <tr>
            <th>LUN ID</th>
            <th>Device</th>
            <th>Size</th>
            <th>Vendor</th>
          </tr>
        </thead>
        <tbody>
          {host.luns.map((l, i) => (
            <tr key={i}>
              <td>{l.lun_id}</td>
              <td>{l.device}</td>
              <td>{l.size}</td>
              <td>{l.vendor}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Mappings */}
      <h4 style={{ marginTop: "24px" }}>HBA ↔ LUN Mappings</h4>
      <table border="1" cellPadding="8" width="100%">
        <thead>
          <tr>
            <th>LUN</th>
            <th>Paths</th>
            <th>HBA WWNs</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {host.mappings.map((m, i) => (
            <tr key={i}>
              <td>{m.lun_id}</td>
              <td>{m.paths}</td>
              <td>{m.hba_wwns.join(", ")}</td>
              <td>{m.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
