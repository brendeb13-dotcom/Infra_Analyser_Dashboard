import { useEffect, useState } from "react";
import { fetchStorageOverview } from "../api/storage";

import StorageKPIs from "../components/StorageKPIs";
import StorageHostsTable from "../components/StorageHostsTable";
import StorageHostDetails from "../components/StorageHostDetails";

/* 🔍 + 📤 shared dashboard utilities */
import GlobalSearchBar from "../components/GlobalSearchBar";
import ExportButton from "../components/ExportButton";
import useGlobalSearch from "../components/useGlobalSearch";

const kpiStyle = {
  border: "1px solid #ccc",
  borderRadius: "8px",
  padding: "12px 20px",
  minWidth: "180px",
};

export default function StorageOverview() {
  const [data, setData] = useState(null);
  const [selectedHost, setSelectedHost] = useState(null);

  /* Global search hook */
  const { query, setQuery, filter } = useGlobalSearch();

  useEffect(() => {
    fetchStorageOverview("demo_client", "dev").then(setData);
  }, []);

  if (!data) return <p>Loading storage data...</p>;

  /* 🔍 Apply global search on hosts + nested fields */
  const filteredHosts = filter(data.hosts, [
    "hostname",
    "ip",
    "luns.lun_id",
    "luns.device",
    "luns.vendor",
    "luns.size"
  ]);

  /* ✅ Total Capacity calculation (approx, GB-based) */
  const totalCapacity = filteredHosts.reduce((sum, h) => {
    return (
      sum +
      h.luns.reduce((s, l) => {
        const size = parseFloat(l.size); // e.g. "100G"
        return isNaN(size) ? s : s + size;
      }, 0)
    );
  }, 0);

  return (
    <div style={{ padding: "24px", fontFamily: "Arial, sans-serif" }}>
      <h2>Storage Overview</h2>

      {/* 🔍 GLOBAL SEARCH */}
      <GlobalSearchBar
        value={query}
        onChange={setQuery}
      />

      {/* 📤 EXPORT */}
      <ExportButton
        data={filteredHosts}
        filename="storage_overview"
      />

      {/* KPI SECTION */}
      <div style={{ display: "flex", gap: "20px", marginBottom: "24px" }}>
        <StorageKPIs summary={{
          ...data.summary,
          hosts: filteredHosts.length
        }} />

        <div style={kpiStyle}>
          <div>Total Capacity (approx)</div>
          <b>{totalCapacity} GB</b>
        </div>
      </div>

      {/* HOST TABLE */}
      <StorageHostsTable
        hosts={filteredHosts}
        onSelect={setSelectedHost}
      />

      {/* HOST DRILL-DOWN */}
      <StorageHostDetails host={selectedHost} />
    </div>
  );
}
