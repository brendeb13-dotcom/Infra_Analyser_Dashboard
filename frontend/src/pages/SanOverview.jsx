import { useEffect, useState } from "react";
import { fetchSanOverview } from "../api/san";

/* 🔍 + 📤 shared dashboard utilities */
import GlobalSearchBar from "../components/GlobalSearchBar";
import ExportButton from "../components/ExportButton";
import useGlobalSearch from "../components/useGlobalSearch";

/* 🎨 Russ Consultancy theme */
const styles = {
  page: {
    padding: "28px",
    fontFamily: "Inter, Arial, sans-serif",
    background: "#F8FAFC",
    minHeight: "100vh"
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "18px"
  },
  title: {
    color: "#1F3A5F",
    fontSize: "1.6rem",
    fontWeight: 700
  },
  toolbar: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginBottom: "20px"
  },
  card: {
    background: "#FFFFFF",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "0 6px 16px rgba(0,0,0,0.06)",
    marginBottom: "24px"
  },
  kpiRow: {
    display: "flex",
    gap: "16px",
    flexWrap: "wrap"
  },
  table: {
    width: "100%",
    borderCollapse: "collapse"
  },
  th: {
    background: "#1F3A5F",
    color: "#FFFFFF",
    padding: "10px",
    textAlign: "left"
  },
  td: {
    padding: "10px",
    borderBottom: "1px solid #E2E8F0"
  }
};

export default function SanOverview() {
  const [data, setData] = useState(null);

  /* Global search */
  const { query, setQuery, filter } = useGlobalSearch();

  useEffect(() => {
    fetchSanOverview("demo_client", "dev").then(setData);
  }, []);

  if (!data) {
    return (
      <div style={styles.page}>
        <p>Loading SAN data…</p>
      </div>
    );
  }

  /* 🔍 Apply global search across SAN fields */
  const filteredHosts = filter(data.hosts, [
    "hostname",
    "ip",
    "fcas.wwn",
    "fcas.id",
    "switches.name",
    "switches.ports.port",
    "lun_mappings.lun_id",
    "lun_mappings.hba_wwn"
  ]);

  /* 🔢 Recalculate KPIs from filtered data */
  const summary = {
    hosts: filteredHosts.length,
    fcas: filteredHosts.reduce((s, h) => s + h.fcas.length, 0),
    switch_ports: filteredHosts.reduce(
      (sum, h) =>
        sum +
        h.switches.reduce(
          (s, sw) => s + (sw.ports?.length || 0),
          0
        ),
      0
    ),
    luns: filteredHosts.reduce(
      (s, h) => s + h.lun_mappings.length,
      0
    ),
  };

  return (
    <div className="container" style={styles.page}>
      {/* HEADER */}
      <div style={styles.header}>
        <h2 style={styles.title}>SAN Overview</h2>
      </div>

      {/* SEARCH + EXPORT */}
      <div style={styles.toolbar}>
        <GlobalSearchBar
          value={query}
          onChange={setQuery}
        />

        <ExportButton
          data={filteredHosts}
          filename="san_overview"
        />
      </div>

      {/* KPIs */}
      <div style={{ ...styles.card, ...styles.kpiRow }}>
        <KPI title="Hosts" value={summary.hosts} />
        <KPI title="FCAs" value={summary.fcas} />
        <KPI title="Switch Ports" value={summary.switch_ports} />
        <KPI title="LUNs" value={summary.luns} />
      </div>

      {/* TABLE */}
      <div style={styles.card}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Host</th>
              <th style={styles.th}>IP</th>
              <th style={styles.th}>FCAs</th>
              <th style={styles.th}>Switch Ports</th>
              <th style={styles.th}>LUN Mappings</th>
              <th style={styles.th}>Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {filteredHosts.map((h) => (
              <tr key={h.hostname}>
                <td style={styles.td}>{h.hostname}</td>
                <td style={styles.td}>{h.ip}</td>
                <td style={styles.td}>{h.fcas.length}</td>
                <td style={styles.td}>
                  {h.switches.reduce(
                    (sum, s) => sum + (s.ports?.length || 0),
                    0
                  )}
                </td>
                <td style={styles.td}>{h.lun_mappings.length}</td>
                <td style={styles.td}>
                  {new Date(h.last_seen).toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function KPI({ title, value }) {
  return (
    <div
      style={{
        border: "1px solid #E2E8F0",
        padding: "14px 18px",
        borderRadius: "10px",
        minWidth: "140px",
        background: "#FFFFFF",
        boxShadow: "0 4px 10px rgba(0,0,0,0.05)"
      }}
    >
      <div style={{ color: "#64748B", fontSize: "0.85rem" }}>
        {title}
      </div>
      <div style={{ color: "#1F3A5F", fontSize: "1.2rem", fontWeight: 700 }}>
        {value}
      </div>
    </div>
  );
}
