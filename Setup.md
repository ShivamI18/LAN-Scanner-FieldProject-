LAN Device Scanner – Full Stack Project

This project is a full-stack Local Area Network (LAN) device scanner that:
• Scans all devices on your local network
• Detects IP and MAC addresses
• Classifies devices into types like Router, Laptop, Mobile Phone, Printer, Camera, Smart TV, and Unknown
• Sends the scan result as JSON to an Express.js backend
• Displays the output in a React (Vite) frontend

This project is designed to work on both macOS and Windows without requiring sudo/administrator access.

---

## Project Architecture

1. Python Scanner (scanner.py)
   • Detects OS automatically (macOS or Windows)
   • Detects active subnet
   • Pings all devices in subnet
   • Reads ARP table
   • Detects device type using network behavior (TTL + routing logic)
   • Outputs only clean JSON to stdout

2. Express.js Backend
   • Exposes an API endpoint
   • Executes the Python scanner
   • Parses JSON output
   • Returns results to frontend
   • Uses CORS for cross-origin access

3. React Frontend (Vite)
   • Button to start scan
   • Fetches device list from backend
   • Displays formatted JSON output
   • Live loading indicator

---

## Features

• Cross-platform support (macOS + Windows)
• No sudo / no raw packet access
• Fast async subnet scanning
• IP + MAC address discovery
• Intelligent device type detection:
– Router
– Laptop / PC
– Mobile Phone
– Printer
– Camera
– Smart TV
– Unknown Device
• Clean JSON API response
• React based UI

---

## How Device Type Detection Works

This project does NOT use:
• Vendor databases
• OUI lookups
• Online APIs

Instead, it uses:
• ICMP TTL behavior
• Network role heuristics
• Broadcast address detection
• Router gateway detection

This makes the system:
• Fully offline
• Private
• Very fast

---

## Installation Overview

Backend Requirements:
• Node.js (v18+ recommended)
• Python 3.9+
• Express.js
• CORS enabled

Frontend Requirements:
• Vite
• React

Python Requirements:
• ipaddress
• subprocess
• asyncio
• platform
• re
• json

---

## ✅ FULL SETUP INSTRUCTIONS

---

1. Clone the Project

---

Create a new folder and place these files:

• scanner.py
• backend (Express folder)
• frontend (Vite React folder)

---

2. Backend Setup (Express.js)

---

Open terminal inside backend folder:

Install dependencies:
• npm init -y
• npm install express cors

Create index.js and add your API logic.

Start backend:
• node index.js

Backend runs on:
• [http://localhost:3000](http://localhost:3000)

---

3. Python Scanner Setup

---

Make sure Python is installed:

Check version:
• python3 --version

Your scanner.py should be in the backend root folder.

Test manually:
• python3 scanner.py

It must print only JSON output.

---

4. Frontend Setup (React + Vite)

---

Open terminal inside frontend folder:

Install dependencies:
• npm install

Start React app:
• npm run dev

Frontend runs on:
• [http://localhost:5173](http://localhost:5173)

---

5. Connect Frontend to Backend

---

Your React app should fetch from:

• [http://localhost:3000/scan](http://localhost:3000/scan)

Make sure:
• Backend is running first
• Then start frontend

---

6. Final Run Order (IMPORTANT)

---

Step 1 → Start Backend
Step 2 → Start Frontend
Step 3 → Open Browser
Step 4 → Click "Scan Now"
Step 5 → Devices appear instantly

---

## Sample Output Format

Each scan returns structured JSON like:

• IP Address
• MAC Address
• Device Type (human readable)

This format is optimized for:
• Dashboards
• Network monitoring
• Visualization
• Security tools

---

## Important Limitations

• Device classification is heuristic-based, not 100% guaranteed
• Some phones and laptops may share similar TTL behavior
• Guest networks and VLANs may block ARP visibility
• Enterprise routers may hide devices

---

## Security Notes

• No data is uploaded to the internet
• Everything works locally
• No packet sniffing
• No root/admin privileges required
• Safe for personal and educational use

---

## Use Cases

• Home network monitoring
• College network projects
• Cybersecurity demonstrations
• Device discovery tools
• IoT scanning
• Ethical hacking labs

---

## Author Notes

This project was built with a strong focus on:
• Performance
• Privacy
• Simplicity
• Cross-platform reliability

No external APIs, no vendor tracking, and no unsafe system access.

---

## Future Improvements

• Real-time auto refresh
• Network mapping UI
• Export to CSV / JSON file
• Improved device fingerprinting
• IPv6 support

---

## License

Free to use for learning, personal projects, and academic research.

---

## End of README
