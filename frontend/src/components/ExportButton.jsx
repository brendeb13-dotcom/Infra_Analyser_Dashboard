export default function ExportButton({ data, filename }) {
  const exportJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json"
    });
    download(blob, `${filename}.json`);
  };

  const exportCSV = () => {
    if (!data.length) return;

    const headers = Object.keys(data[0]);
    const rows = data.map(d =>
      headers.map(h => JSON.stringify(d[h] ?? "")).join(",")
    );

    const csv = [headers.join(","), ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });

    download(blob, `${filename}.csv`);
  };

  const download = (blob, name) => {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ marginBottom: "16px" }}>
      <button onClick={exportCSV}>Export CSV</button>
      <button onClick={exportJSON} style={{ marginLeft: "8px" }}>
        Export JSON
      </button>
    </div>
  );
}
