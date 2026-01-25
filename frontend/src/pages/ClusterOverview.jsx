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

  if (!overview) return <p>Loading cluster data…</p>;

  /* 🔍 Apply global search */
  const filteredClusters = filter(overview.clusters, [
    "name",
    "type",
    "nodes",
    "last_seen"
  ]);

  return (
    <div style={{ padding: "24px" }}>
      <h2>Cluster Overview</h2>

      {/* 🔍 GLOBAL SEARCH */}
      <GlobalSearchBar
        value={query}
        onChange={setQuery}
      />

      {/* 📤 EXPORT */}
      <ExportButton
        data={filteredClusters}
        filename="cluster_overview"
      />

      {/* 📊 KPIs */}
      <ClusterKPIs clusters={filteredClusters} />

      {/* 📋 TABLE */}
      <ClusterTable
        clusters={filteredClusters}
        onSelect={onSelect}
      />

      {/* 🔎 NODE DETAILS */}
      <ClusterNodeDetails cluster={selectedCluster} />
    </div>
  );
}
