export default function ClusterNodeDetails({ cluster }) {
  if (!cluster || !cluster.nodes) return null;

  return (
    <div>
      <h3>Cluster: {cluster.name}</h3>

      {cluster.nodes.map((node, index) => (
        <div
          key={node.hostname || index}
          style={{
            border: "1px solid #e5e7eb",
            padding: "16px",
            marginBottom: "20px",
            borderRadius: "10px",
            background: "#ffffff",
          }}
        >
          <h4 style={{ marginBottom: "6px" }}>
            {node.hostname} ({node.ip})
          </h4>

          <p style={{ marginBottom: "12px" }}>
            <strong>Role:</strong> {node.role || "N/A"}
          </p>

          {/* ========================= */}
          {/* 🔥 APPLICATION MAPPING */}
          {/* ========================= */}
          <h5 style={{ marginBottom: "8px" }}>Application Mapping</h5>

          {node.app_mount_mapping && node.app_mount_mapping.length > 0 ? (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginBottom: "16px",
              }}
            >
              <thead>
                <tr style={{ background: "#f3f4f6" }}>
                  <th style={thStyle}>Server</th>
                  <th style={thStyle}>Mount Point</th>
                  <th style={thStyle}>Application</th>
                </tr>
              </thead>
              <tbody>
                {node.app_mount_mapping.map((m, i) => (
                  <tr key={i}>
                    <td style={tdStyle}>{node.hostname}</td>
                    <td style={tdStyle}>{m.path}</td>
                    <td style={tdStyle}>
                      {m.application}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ marginBottom: "16px" }}>
              No mount mapping available
            </p>
          )}

          {/* ========================= */}
          {/* 📦 APPLICATIONS */}
          {/* ========================= */}
          <h5 style={{ marginBottom: "8px" }}>Processes</h5>

          {node.apps && node.apps.length > 0 ? (
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
              }}
            >
              <thead>
                <tr style={{ background: "#f3f4f6" }}>
                  <th style={thStyle}>Process Name</th>
                  <th style={thStyle}>Type</th>
                  <th style={thStyle}>Status</th>
                  <th style={thStyle}>Ports</th>
                </tr>
              </thead>
              <tbody>
                {node.apps.map((app, idx) => (
                  <tr key={idx}>
                    <td style={tdStyle}>{app.name}</td>
                    <td style={tdStyle}>{app.type}</td>
                    <td style={tdStyle}>{app.status}</td>
                    <td style={tdStyle}>
                      {app.ports?.length > 0
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

/* ========================= */
/* 🎨 STYLES */
/* ========================= */

const thStyle = {
  padding: "10px",
  border: "1px solid #e5e7eb",
  textAlign: "left",
  fontWeight: "600",
};

const tdStyle = {
  padding: "10px",
  border: "1px solid #e5e7eb",
};