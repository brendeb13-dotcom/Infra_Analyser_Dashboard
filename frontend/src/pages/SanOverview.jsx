import { useEffect, useState } from "react";
import { fetchSanOverview } from "../api/san";

/* 🔍 + 📤 shared dashboard utilities */
import GlobalSearchBar from "../components/GlobalSearchBar";
import ExportButton from "../components/ExportButton";
import useGlobalSearch from "../components/useGlobalSearch";

export default function SanOverview() {
  const [data, setData] = useState(null);

  /* Global search */
  const { query, setQuery, filter } = useGlobalSearch();

  useEffect(() => {
    fetchSanOverview("demo_client", "dev").then(setData);
  }, []);

  if (!data) return <p>Loading SAN data...</p>;

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
    <div style={{ padding: "24px" }}>
      <h2>SAN Overview</h2>

      {/* 🔍 GLOBAL SEARCH */}
      <GlobalSearchBar
        value={query}
        onChange={setQuery}
      />

      {/* 📤 EXPORT */}
      <ExportButton
        data={filteredHosts}
        filename="san_overview"
      />

      {/* KPI ROW */}
      <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
        <KPI title="Hosts" value={summary.hosts} />
        <KPI title="FCAs" value={summary.fcas} />
        <KPI title="Switch Ports" value={summary.switch_ports} />
        <KPI title="LUNs" value={summary.luns} />
      </div>

      {/* HOST TABLE */}
      <table border="1" cellPadding="8" width="100%">
        <thead>
          <tr>
            <th>Host</th>
            <th>IP</th>
            <th>FCAs</th>
            <th>Switch Ports</th>
            <th>LUN Mappings</th>
            <th>Last Seen</th>
          </tr>
        </thead>
        <tbody>
          {filteredHosts.map((h) => (
            <tr key={h.hostname}>
              <td>{h.hostname}</td>
              <td>{h.ip}</td>
              <td>{h.fcas.length}</td>
              <td>
                {h.switches.reduce(
                  (sum, s) => sum + (s.ports?.length || 0),
                  0
                )}
              </td>
              <td>{h.lun_mappings.length}</td>
              <td>{new Date(h.last_seen).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KPI({ title, value }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "12px",
        borderRadius: "8px",
        minWidth: "120px",
      }}
    >
      <div>{title}</div>
      <b>{value}</b>
    </div>
  );
}
