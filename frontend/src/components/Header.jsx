import logo from "../assets/logo.jpg";

export default function Header() {
  return (
    <div style={styles.header}>
      <div style={styles.left}>
        <img src={logo} alt="Russ Consultancy" style={styles.logo} />
        <span style={styles.title}>
          Infrastructure Analyzer
        </span>
      </div>
    </div>
  );
}

const styles = {
  header: {
    height: "64px",
    backgroundColor: "#063970", // Catalina Blue
    display: "flex",
    alignItems: "center",
    padding: "0 24px",
    boxShadow: "0 2px 6px rgba(0,0,0,0.15)",
  },
  left: {
    display: "flex",
    alignItems: "center",
    gap: "14px",
  },
  logo: {
    height: "40px",
  },
  title: {
    color: "#ffffff",
    fontSize: "18px",
    fontWeight: "600",
    letterSpacing: "0.5px",
  },
};
