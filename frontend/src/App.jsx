import { useEffect, useState } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

/* ---------- Small reusable component ---------- */
function StatusBadge({ status }) {
  const colors = {
    OK: "#2e7d32",
    WARN: "#ed6c02",
    FAIL: "#d32f2f",
    UNKNOWN: "#6c757d",
  };

  return (
    <span
      style={{
        padding: "4px 10px",
        borderRadius: "12px",
        color: "white",
        backgroundColor: colors[status] || "#6c757d",
        fontWeight: 600,
        fontSize: "0.85rem",
      }}
    >
      {status}
    </span>
  );
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get(
        `${API_BASE}/api/v1/overview?client_id=demo_client&environment=dev`
      )
      .then((res) => setData(res.data))
      .catch(() => setError("Unable to load overview data"));
  }, []);

  if (error) {
    return <h3 style={{ color: "red" }}>{error}</h3>;
  }

  if (!data) {
    return <h3>Loading infrastructure health…</h3>;
  }

  const capabilities = data.capabilities || [];

  /* ---------- KPI COMPUTATIONS (A1) ---------- */
  const totalChecks = capabilities.length;

  const okChecks = capabilities.filter(
    (c) => c.status === "OK"
  ).length;

  const failChecks = capabilities.filter(
    (c) => c.status === "FAIL"
  ).length;

  const totalAffectedHosts = capabilities.reduce(
    (sum, c) => sum + (c.affected_hosts || 0),
    0
  );

  const overallStatus = capabilities.some((c) => c.status === "FAIL")
    ? "FAIL"
    : capabilities.some((c) => c.status === "WARN")
    ? "WARN"
    : "OK";

  const lastUpdate =
    capabilities.length > 0
      ? new Date(
          Math.max(
            ...capabilities.map((c) =>
              new Date(c.last_run).getTime()
            )
          )
        ).toLocaleString()
      : "N/A";

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif" }}>
      <h2>Infrastructure Health Overview</h2>
      <p>
        Client: <b>{data.client_id}</b> | Environment:{" "}
        <b>{data.environment}</b>
      </p>

      {/* ---------- KPI CARDS ---------- */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
        <div style={kpiStyle}>
          <div>Total Checks</div>
          <b>{totalChecks}</b>
        </div>

        <div style={kpiStyle}>
          <div>OK</div>
          <b style={{ color: "#2e7d32" }}>{okChecks}</b>
        </div>

        <div style={kpiStyle}>
          <div>FAIL</div>
          <b style={{ color: "#d32f2f" }}>{failChecks}</b>
        </div>

        <div style={kpiStyle}>
          <div>Overall Status</div>
          <StatusBadge status={overallStatus} />
        </div>

        <div style={kpiStyle}>
          <div>Affected Hosts</div>
          <b>{totalAffectedHosts}</b>
        </div>

        <div style={kpiStyle}>
          <div>Last Update</div>
          <b>{lastUpdate}</b>
        </div>
      </div>

      {/* ---------- TABLE ---------- */}
      {capabilities.length === 0 ? (
        <p>No health data available yet.</p>
      ) : (
        <table
          border="1"
          cellPadding="10"
          style={{ borderCollapse: "collapse", width: "100%" }}
        >
          <thead>
            <tr>
              <th>Capability</th>
              <th>Status</th>
              <th>Affected Hosts</th>
              <th>Last Run</th>
            </tr>
          </thead>
          <tbody>
            {capabilities.map((cap) => (
              <tr key={cap.category}>
                <td>{cap.name}</td>
                <td>
                  <StatusBadge status={cap.status} />
                </td>
                <td>{cap.affected_hosts}</td>
                <td>{new Date(cap.last_run).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

const kpiStyle = {
  border: "1px solid #ccc",
  borderRadius: "8px",
  padding: "12px 20px",
  minWidth: "160px",
  textAlign: "center",
};
