export default function ClusterNodeDetails({ cluster }) {
  if (!cluster) return null;

  return (
    <div>
      <h3>Cluster: {cluster.name}</h3>

      {cluster.nodes.map((node) => (
        <div
          key={node.hostname}
          style={{
            border: "1px solid #ccc",
            padding: "12px",
            marginBottom: "16px",
            borderRadius: "6px"
          }}
        >
          <h4>
            {node.hostname} ({node.ip})
          </h4>
          <p>Role: {node.role}</p>

          <h5>Applications</h5>

          {node.apps && node.apps.length > 0 ? (
            <table border="1" cellPadding="8" width="100%">
              <thead>
                <tr>
                  <th>App Name</th>
                  <th>Type</th>
                  <th>Status</th>
                  <th>Ports</th>
                </tr>
              </thead>
              <tbody>
                {node.apps.map((app, idx) => (
                  <tr key={idx}>
                    <td>{app.name}</td>
                    <td>{app.type}</td>
                    <td>{app.status}</td>
                    <td>
                      {app.ports && app.ports.length > 0
                        ? app.ports.join(", ")
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No applications detected</p>
          )}
        </div>
      ))}
    </div>
  );
}
