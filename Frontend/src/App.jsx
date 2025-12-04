import { useState,useEffect } from "react";
import "./App.css";

function App() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(false);

  const scanNetwork = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:3000/scan", { method: "POST" });
      const data = await res.json();
      setDevices(Array.isArray(data) ? data : []);
    } catch (e) {
      alert("❌ Scan failed — server returned no JSON");
      setDevices([]);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>LAN Device Scanner</h2>
      <button onClick={scanNetwork} disabled={loading} >
        {loading ? "Scanning..." : "Scan Now"}
      </button>
      <pre>
        {devices.length ? JSON.stringify(devices, null, 2) : "No scan yet"}
      </pre>
    </div>
  );
}

export default App;
