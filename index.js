import { exec } from "child_process";
import express from "express";
import cors from "cors";
// import fetch from "node-fetch";

const app = express();

app.use(cors({ origin: "http://localhost:5173" })); // allow frontend
app.use(express.json());

// Run scanner
app.post("/scan", (req, res) => {
  exec("python3 scanner.py", (err, stdout) => {
    if (err) return res.status(500).json({ error: "Scan failed" });

    try {
      res.json(JSON.parse(stdout));
    } catch {
      res.status(500).json({ error: "Invalid JSON returned" });
    }
  });
});


app.listen(3000, () => console.log("API → http://localhost:3000"));
