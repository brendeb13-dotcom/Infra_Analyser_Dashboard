import { useEffect, useState } from "react";
import { fetchStorageOverview } from "../api/storage";

import StorageKPIs from "../components/StorageKPIs";
import StorageHostsTable from "../components/StorageHostsTable";
import StorageHostDetails from "../components/StorageHostDetails";

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
    minHeight: "100vh",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "18px",
  },
  title: {
    color: "#1F3A5F",
    fontSize: "1.6rem",
    fontWeight: 700,
  },
  toolbar: {
    display: "flex",
    gap: "12px",
    alignItems: "center",
    marginBottom: "22px",
  },
  card: {
    background: "#FFFFFF",
    borderRadius: "12px",
    padding: "20px",
    boxShadow: "0 6px 16px rgba(0,0,0,0.06)",
    marginBottom: "24px",
  },
  kpiRow: {
    display: "flex",
    gap: "20px",
    flexWrap: "wrap",
  },
  capacityCard: {
    border: "1px solid #E2E8F0",
    borderRadius: "10px",
    padding: "14px 18px",
    minWidth: "180px",
    background: "#FFFFFF",
    boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
  },
  capacityLabel: {
    color: "#64748B",
    fontSize: "0.85rem",
  },
  capacityValue: {
    color: "#1F3A5F",
    fontSize: "1.2rem",
    fontWeight: 700,
  },
};

export default function StorageOverview() {
  const [data, setData] = useState(null);
  const [selectedHost, setSelectedHost] = useState(null);

  /* Global search hook */
  const { query, setQuery, filter } = useGlobalSearch();

  useEffect(() => {
    fetchStorageOverview("demo_client", "dev").then(setData);
  }, []);

  if (!data) {
    return (
      <div style={styles.page}>
        <p>Loading storage data…</p>
      </div>
    );
  }

  /* 🔍 Apply global search on hosts + nested fields */
  const filteredHosts = filter(data.hosts, [
    "hostname",
    "ip",
    "os",
    "luns.lun_id",
    "luns.device",
    "luns.vendor",
    "luns.size",
  ]);

  /* ✅ Total Capacity calculation (approx, GB-based) */
  const totalCapacity = filteredHosts.reduce(
  (sum, h) => sum + (h.total_capacity_gb || 0),
  0
);

  return (
    <div className="container" style={styles.page}>
      {/* HEADER */}
      <div style={styles.header}>
        <h2 style={styles.title}>Storage Overview</h2>
      </div>

      {/* SEARCH + EXPORT */}
      <div style={styles.toolbar}>
        <GlobalSearchBar
          value={query}
          onChange={setQuery}
        />

        <ExportButton
          data={filteredHosts}
          filename="storage_overview"
        />
      </div>

      {/* KPI SECTION */}
      <div style={{ ...styles.card, ...styles.kpiRow }}>
        <StorageKPIs
          summary={{
            ...data.summary,
            hosts: filteredHosts.length,
          }}
        />

        <div style={styles.capacityCard}>
          <div style={styles.capacityLabel}>
            Total Capacity (approx)
          </div>
          <div style={styles.capacityValue}>
            {totalCapacity} GB
          </div>
        </div>
      </div>

      {/* HOST TABLE */}
      <div style={styles.card}>
        <StorageHostsTable
          hosts={filteredHosts}
          onSelect={setSelectedHost}
        />
      </div>

      {/* HOST DRILL-DOWN */}
      <div style={styles.card}>
        <StorageHostDetails host={selectedHost} />
      </div>
    </div>
  );
}
