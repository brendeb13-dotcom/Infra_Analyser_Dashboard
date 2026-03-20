export default function ExportButton({ data, filename }) {
  const exportToCsv = () => {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const rows = data.map(row =>
      headers.map(h => JSON.stringify(row[h] ?? "")).join(",")
    );

    const csvContent =
      headers.join(",") + "\n" + rows.join("\n");

    const blob = new Blob([csvContent], {
      type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${filename}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={exportToCsv}
      style={{
        background: "#1D7A8C",
        color: "white",
        padding: "8px 14px",
        borderRadius: "6px",
        border: "none",
        cursor: "pointer",
        fontWeight: 600,
        marginBottom: "16px",
        marginLeft: "12px"
      }}
    >
      Download CSV
    </button>
  );
}
