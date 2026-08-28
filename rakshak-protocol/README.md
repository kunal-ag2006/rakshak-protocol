# 🛡️ Rakshak Protocol (रक्षक)
> **Zero-Click SOS & Autonomous Police Drone Dispatch System**  
> *Built for hackathons, emergency response systems, and next-gen civic safety.*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 💡 Why I Built This

Most emergency SOS apps on the market share one fatal flaw: **they require you to unlock your phone, open an app, or press a button on a screen.** 

In actual violent ambushes, kidnappings, or medical emergencies, victims often have zero access to their phone screen. 

The **Rakshak Protocol** solves this by introducing a **Zero-Click Threat Pipeline**:
1. **Smartwatch PPG/HRV Triage:** Detects extreme physiological panic (heart rate surging above 150 BPM combined with a near-zero HRV drop).
2. **On-Device TinyML Acoustic Classifier:** Listens in low-power mode for distress signals (screams, glass breaks, gunshots, panic phrases).
3. **Stealth SOS Activation:** When both conditions converge, the phone screen stays completely pitch black (so attackers don't know an alert was sent) while silently streaming encrypted GPS, vitals, and audio chunks over MQTT.
4. **Autonomous Cell-Tower Drone Dispatch:** Locates the nearest drone dock mounted on telecom towers (Airtel/Jio 5G towers) and launches a high-speed quadcopter to the exact GPS coordinates in **under 60 seconds** to flash high-intensity strobes, sound a siren, and stream 4K video to police before patrol cars can arrive.
5. **Cryptographic Evidence Vault:** Hashes each telemetry and audio packet into a tamper-proof SHA-256 ledger so evidence cannot be deleted or modified in court.

---

## 🛠️ Architecture

```
[ Citizen Wearable / Phone ]
    ├── PPG / HRV Sensor (Heart Rate Spike + HRV Collapse)
    ├── TinyML Acoustic Model (Screams, Gunshots, Panic Keywords)
    └── 3-Second Physical Power Key (Manual Hardware Interrupt)
                 │
                 ▼ (Multi-Factor Danger Gate)
         [ Stealth SOS Mode ]  <-- Screen stays 100% BLACK
                 │
                 ▼ Encrypted MQTT Uplink (QoS 2)
     [ Rakshak Ingestion Gateway & Server ]
         ├── Spatial Drone Router (Calculates nearest cell tower dock)
         └── SHA-256 Cryptographic Evidence Vault (Immutable chain)
                 │
                 ▼ Dispatches in < 60s
     [ Autonomous Drone Station (Tower-Mounted) ]
         ├── Rapid Takeoff & High-Speed Transit (80 km/h)
         ├── High-Decibel Acoustic Siren & Strobe Deterrent
         └── Live 4K Optical/Thermal Stream to Police EOC
```

---

## 🚀 Quickstart (Run Locally)

### 1. Clone & Setup Environment
```bash
git clone https://github.com/kunal-ag2006/rakshak-protocol.git
cd rakshak-protocol

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the Server & Web Dashboard
```bash
python -m uvicorn server.app.main:app --reload
```
Open your browser and head to:
👉 **`http://127.0.0.1:8000`**

### 3. Run the CLI Simulation
In a second terminal window:
```bash
python scripts/run_demo.py
```

---

## 🎮 Web Dashboard Controls
- Click **`🚨 Trigger Ambush & Auto-Fly`** (or press **Spacebar**) to simulate an emergency and watch the drone fly across the radar in real time.
- Click **`⚡ 3s Button SOS`** to test hardware button override.
- Click **`🔄 Reset Baseline`** (or press **R**) to reset to normal heartbeat.
- Click **`🔒 Verify Hash-Chain Integrity`** to run a cryptographic audit on all evidence blocks.

---

## 📂 Project Layout

```text
rakshak-protocol/
├── edge_device/           # Wearable PPG/HRV & TinyML audio inference logic
│   ├── biometric_engine.py
│   ├── acoustic_engine.py
│   ├── stealth_controller.py
│   └── hardware_interrupt.py
├── server/                # FastAPI backend & Tactical Dashboard
│   ├── app/
│   │   ├── main.py        # API endpoints & WebSocket feed
│   │   ├── drone_router.py# Spatial distance calculation & dock dispatch
│   │   └── evidence_vault.py # SHA-256 tamper-proof evidence ledger
│   └── templates/
│       └── index.html     # 60 FPS HTML5 Canvas tactical radar & telemetry HUD
├── simulations/           # Scenario runner & synthetic attack datasets
│   ├── run_scenario.py
│   └── mock_data.py
├── tests/                 # Unit test suite (17/17 tests passing)
├── scripts/               # Helper scripts (run_demo.py, deploy_local.sh)
└── requirements.txt
```

---

## 🧪 Testing

Run the full test suite with:
```bash
python -m unittest discover tests
```

---

## 📜 License
MIT License. Built for open-source civic safety research and hackathon implementations.
