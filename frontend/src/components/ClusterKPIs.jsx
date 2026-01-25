export default function ClusterKPIs({ clusters }) {
  const totalClusters = clusters.length;
  const totalNodes = clusters.reduce(
    (sum, c) => sum + c.nodes,
    0
  );

  return (
    <div style={{ display: "flex", gap: "16px", marginBottom: "24px" }}>
      <div className="kpi-card">
        <h4>Clusters</h4>
        <b>{totalClusters}</b>
      </div>

      <div className="kpi-card">
        <h4>Total Nodes</h4>
        <b>{totalNodes}</b>
      </div>
    </div>
  );
}
