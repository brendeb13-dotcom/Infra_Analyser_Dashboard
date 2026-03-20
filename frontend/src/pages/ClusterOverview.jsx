import { useEffect, useState } from "react";
import {
  fetchClusterOverview,
  fetchClusterDetails
} from "../api/cluster";

import ClusterKPIs from "../components/ClusterKPIs";
import ClusterTable from "../components/ClusterTable";
import ClusterNodeDetails from "../components/ClusterNodeDetails";

/* 🔍 + 📤 shared components */
import GlobalSearchBar from "../components/GlobalSearchBar";
import ExportButton from "../components/ExportButton";
import useGlobalSearch from "../components/useGlobalSearch";

/* 🎨 Russ Consultancy palette */
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
  subtext: {
    color: "#64748B",
    fontSize: "0.9rem"
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
  }
};

export default function ClusterOverview() {
  const [overview, setOverview] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState(null);

  /* Global search hook */
  const { query, setQuery, filter } = useGlobalSearch();

  useEffect(() => {
    fetchClusterOverview("demo_client", "dev")
      .then(setOverview);
  }, []);

  const onSelect = async (clusterName) => {
    const details = await fetchClusterDetails(
      clusterName,
      "demo_client",
      "dev"
    );
    setSelectedCluster(details.cluster);
  };

  if (!overview) {
    return (
      <div style={styles.page}>
        <p>Loading cluster data…</p>
      </div>
    );
  }

  /* 🔍 Apply global search */
  const filteredClusters = filter(overview.clusters, [
    "name",
    "type",
    "nodes",
    "last_seen"
  ]);

  return (
    <div className="container" style={styles.page}>
      {/* HEADER */}
      <div style={styles.header}>
        <div>
          <h2 style={styles.title}>Cluster Overview</h2>
          <div style={styles.subtext}>
            Client: <b>demo_client</b> | Environment: <b>dev</b>
          </div>
        </div>
      </div>

      {/* SEARCH + EXPORT */}
      <div style={styles.toolbar}>
        <GlobalSearchBar
          value={query}
          onChange={setQuery}
        />

        <ExportButton
          data={filteredClusters}
          filename="cluster_overview"
        />
      </div>

      {/* KPI CARDS */}
      <div style={styles.card}>
        <ClusterKPIs clusters={filteredClusters} />
      </div>

      {/* CLUSTER TABLE */}
      <div style={styles.card}>
        <ClusterTable
          clusters={filteredClusters}
          onSelect={onSelect}
        />
      </div>

      {/* NODE / APP DETAILS */}
      <div style={styles.card}>
        <ClusterNodeDetails cluster={selectedCluster} />
      </div>
    </div>
  );
}
