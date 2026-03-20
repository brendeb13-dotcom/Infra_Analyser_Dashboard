import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Header from "./components/Header";
import StorageOverview from "./pages/StorageOverview";
import SanOverview from "./pages/SanOverview";
import ClusterOverview from "./pages/ClusterOverview";

export default function App() {
  return (
    <BrowserRouter>
    <Header />
      <div className="container">
        <h2>Dashboard</h2>

        {/* NAV */}
        <nav style={{ marginBottom: "20px" }}>
          <Link to="/" style={linkStyle}>Storage</Link>
          <Link to="/san" style={linkStyle}>SAN</Link>
          <Link to="/cluster" style={linkStyle}>Cluster & Apps</Link>
        </nav>

        <Routes>
          <Route path="/" element={<StorageOverview />} />
          <Route path="/san" element={<SanOverview />} />
          <Route path="/cluster" element={<ClusterOverview />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

const linkStyle = {
  marginRight: "16px",
  textDecoration: "none",
  fontWeight: "bold",
};
