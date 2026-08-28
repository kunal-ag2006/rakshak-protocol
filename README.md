<div align="center">

# 🛡️ Rakshak Protocol
### Autonomous Zero-Click Emergency SOS & Police Drone Dispatch
**Module 3 of Project TransparentGov — Next-Generation Civic Accountability Framework**

[![CI Pipeline](https://img.shields.io/badge/CI-Passing-brightgreen.svg)](.github/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](pyproject.toml)
[![Architecture](https://img.shields.io/badge/Architecture-Edge_AI_%2B_MQTT_%2B_MAVLink-orange.svg)](docs/ARCHITECTURE.md)
[![FastAPI](https://img.shields.io/badge/API-FastAPI_%2B_WebSocket-teal.svg)](server/app/main.py)

*A proactive, code-enforced emergency response system designed for life-threatening situations where victims cannot manually unlock their devices.*

[Architecture](docs/ARCHITECTURE.md) • [Protocol Spec](docs/PROTOCOL_SPEC.md) • [Hardware Guide](docs/HARDWARE_INTEGRATION.md) • [Hackathon Guide](docs/HACKATHON_GUIDE.md)

</div>

---

## 📌 Executive Summary
Traditional emergency SOS solutions rely on manual victim input (unlocking phones, dialling numbers, or opening apps). In situations of kidnapping, assault, or sudden medical incapacitation, this manual requirement fails.

The **Rakshak Protocol** shifts emergency response to an autonomous, multi-factor machine-evaluated paradigm:
1. **Multi-Factor Threat Triage (Zero-Click)**: Continuously evaluates on-device **Wearable Biometrics (PPG/HRV)** and **TinyML Acoustic Anomaly Models** in real time.
2. **Stealth SOS Activation**: Keeps device screens completely off (0 nits) without haptic cues, silently streaming GPS and compressed audio over secure MQTT to prevent perpetrator detection.
3. **Sub-3-Minute Police Drone Dispatch**: Instantly calculates the nearest cell-tower docking station and deploys autonomous deterrence drones equipped with high-intensity visual strobes, sirens, and 4K optical/thermal tracking.
4. **Tamper-Evident Evidence Vault**: Appends all sensor streams into an immutable SHA-256 cryptographic chain, guaranteeing judicial integrity and mathematical non-repudiation.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                            EDGE LAYER (Wearable + Smartphone)                     |
|                                                                                   |
|  [PPG / HRV Sensor]           [Microphone (16kHz)]          [Hardware Power Key] |
|          |                            |                             |             |
|          v                            v                             v             |
|  +--------------------+      +--------------------+      +---------------------+  |
|  | Biometric Triage   |      | TinyML Acoustic    |      | OS-Level Interrupt  |  |
|  | HR > 150 BPM &     |      | Scream / Gunshot / |      | 3-Second Hold /     |  |
|  | RMSSD < 18ms       |      | Glass Break / Panic|      | Panic Multi-Tap     |  |
|  +--------------------+      +--------------------+      +---------------------+  |
|          \                            /                             /             |
|           \                          /                             /              |
|            v                        v                             v               |
|      +--------------------------------------------------------------------+       |
|      |               Stealth SOS Multi-Factor Decision Engine             |       |
|      |       Condition: (BioThreat AND AcousticThreat) OR HardwareHold    |       |
|      +--------------------------------------------------------------------+       |
|                                       |                                           |
|                         [State -> STEALTH_SOS_ACTIVE]                             |
|                                       |                                           |
|             +-------------------------+-------------------------+                 |
|             | Screen Blackout (0 nits)| Silent Mic & GPS Stream |                 |
|             +-------------------------+-------------------------+                 |
|                                       |                                           |
|                              [MQTT Telemetry / HMAC]                              |
+---------------------------------------|-------------------------------------------+
                                        |
                                        v (Cellular 5G / IoT Mesh / QoS 2)
+-----------------------------------------------------------------------------------+
|                        CLOUD VAULT & DISPATCH ENGINE                              |
|                                                                                   |
|  +--------------------------------+       +------------------------------------+  |
|  | Cryptographic Evidence Vault   |       | Drone Spatial Router               |  |
|  | - SHA-256 Hash Chaining        |       | - Cell Tower Base Dock Registry    |  |
|  | - Append-Only Audit Ledger     |       | - Haversine Nearest Dock Selection |  |
|  | - Tamper-Proof Judicial Proof  |       | - Sub-3-Minute Trajectory & ETA    |  |
|  +--------------------------------+       +------------------------------------+  |
|                 |                                           |                     |
|                 +---------------------+---------------------+                     |
|                                       |                                           |
|                                       v                                           |
|                       FastAPI REST & WebSocket Server                             |
+---------------------------------------|-------------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v (MAVLink / 5G Link)                         v (WebSocket Stream)
+-----------------------------------+         +-------------------------------------+
|   AUTONOMOUS POLICE DRONE UNIT    |         | EMERGENCY OPERATIONS CENTER (EOC)   |
|   (Docked at nearest Cell Tower)  |         |                                     |
|   - Rapid Scramble (<10s launch)  |         | - Real-Time Vitals Stream (HR/HRV)  |
|   - 80 km/h Cruise to Target GPS  |         | - Acoustic Spectral Classifier      |
|   - High-Intensity Strobe Lighting|         | - Live Drone Flight Radar & Video   |
|   - 110dB Audio Siren & Speaker   |         | - Cryptographic Ledger Verification |
|   - 4K Optical/Thermal Gimbal Lock|         | - Integrated Police Cruiser Dispatch|
+-----------------------------------+         +-------------------------------------+
```

---

## ⚡ Key Innovations & Modules

### 1. Multi-Factor Authentication for Threat (Zero-Click Triage)
To eliminate false alarms without risking lives, danger is verified across independent physiological and acoustic domains:
- **Condition A (Physiological Distress)**: Instantaneous heart rate surge ($\text{HR} > 150 \text{ BPM}$) accompanied by severe parasympathetic collapse ($\text{RMSSD} \le 18 \text{ ms}$). Aerobic exercise is filtered out using 3-axis accelerometer cadence matching.
- **Condition B (Acoustic Anomaly)**: Low-power on-device TinyML model classifies shrieking (spectral centroid $> 1800\text{ Hz}$), gunshots/explosions (impulsive crest factor $> 5.5$), glass shatter, or spoken panic distress keywords (*"Bachao"*, *"Help me"*).
- **Condition C (Hardware Override)**: 3-second long-press on physical phone side keys bypasses locked touchscreens directly at the OS kernel level.

### 2. Stealth Transmission Engine
- Keeps mobile AMOLED displays powered off ($0\text{ nits}$) with silent tactile haptics.
- Transmits compact JSON/binary telemetry frames over MQTT signed with **HMAC-SHA256**.

### 3. Nearest Cell-Tower Drone Scrambler
- Maintains an urban registry of autonomous drone docks integrated atop cellular base towers.
- Calculates optimal flight trajectories using Great Circle distance (Haversine) with sub-3-minute arrival at $80\text{ km/h}$.
- Automatically activates non-lethal tactical deterrence: 15,000-lumen visual strobe flasher, 110dB siren, and dual optical/thermal gimbal tracking.

### 4. Cryptographic Evidence Vault (Judicial Admissibility)
- Each telemetry block is hashed with SHA-256 and chained to the previous block:
  $$H_i = \text{SHA256}\Big( i \parallel \text{IncidentID} \parallel T_i \parallel H_{i-1} \parallel \text{SHA256}(\text{Telemetry}_i) \parallel \text{SHA256}(\text{AudioChunk}_i) \Big)$$
- Built-in verification engine mathematically proves that no government official, officer, or bad actor altered timestamps, audio records, or GPS coordinates.

---

## 📂 Repository Structure

```
rakshak-protocol/
├── .github/
│   ├── workflows/ci.yml             # GitHub Actions CI Workflow
│   ├── ISSUE_TEMPLATE/              # Standardized Issue Templates
│   └── PULL_REQUEST_TEMPLATE.md     # PR Review Template
├── docs/
│   ├── ARCHITECTURE.md              # Detailed Architectural Specifications
│   ├── PROTOCOL_SPEC.md             # MQTT Schema & HMAC Specifications
│   ├── HARDWARE_INTEGRATION.md      # Wearable SDKs & Drone Flight Controller Guide
│   └── HACKATHON_GUIDE.md           # Presentation, Pitch & Demo Walkthrough
├── edge_device/
│   ├── acoustic_engine.py           # TinyML Audio Classifier (Screams, Gunshots, Keywords)
│   ├── biometric_engine.py          # PPG / HRV Sliding Window Triage
│   ├── hardware_interrupt.py        # 3-Second Physical Button Listener
│   ├── stealth_controller.py        # Threat State Machine & Stealth Mode Enforcer
│   └── mqtt_publisher.py            # Secure Telemetry Streaming Client
├── server/
│   ├── app/
│   │   ├── main.py                  # FastAPI REST API & WebSocket Server
│   │   ├── config.py                # System Environment Configuration
│   │   ├── models.py                # Pydantic Schemas & Telemetry Models
│   │   ├── evidence_vault.py        # Cryptographic Append-Only Ledger (SHA-256)
│   │   ├── drone_router.py          # Spatial Nearest-Tower Drone Allocation & MAVLink
│   │   └── mqtt_broker.py           # Real-Time Telemetry Ingestion & Broadcaster
│   ├── static/                      # Dispatch Console Assets (CSS / JS)
│   └── templates/index.html         # Emergency Operations Center Web Dashboard
├── drone_station/
│   └── drone_simulator.py           # Autonomous Cell-Tower Drone Flight Dynamics
├── simulations/
│   ├── mock_data.py                 # Synthetic Waveforms & Biosignals
│   └── run_scenario.py              # Interactive CLI End-to-End Demo Runner
├── tests/
│   ├── test_biometric.py            # Unit Tests for HRV & Exercise Filtering
│   ├── test_acoustic.py             # Unit Tests for Acoustic Anomaly Engine
│   ├── test_stealth_sos.py          # Unit Tests for Multi-Factor State Machine
│   ├── test_evidence_vault.py       # Unit Tests for Hash Chain Verification & Tamper Detection
│   ├── test_drone_router.py         # Unit Tests for Spatial Allocation & Flight Arrival
│   └── test_api.py                  # Integration Tests for REST Endpoints
├── docker-compose.yml               # Multi-Container Compose Setup
├── Dockerfile                       # Container Definition
├── pyproject.toml                   # Python Packaging Configuration
├── requirements.txt                 # Project Dependencies
├── LICENSE                          # Apache License 2.0
└── README.md                        # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.10+
- `pip` or `docker`

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/transparentgov/rakshak-protocol.git
cd rakshak-protocol

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s tests -p "test_*.py"
```

### 4. Run Interactive CLI Simulation
Run the complete end-to-end simulation showing normal state, exercise resistance, violent ambush trigger, drone transit, on-scene deterrence, and cryptographic chain audit:
```bash
python simulations/run_scenario.py
```

### 5. Launch Emergency Operations Center (EOC) Dashboard
```bash
uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to **`http://localhost:8000`** to access the live tactical command center.

---

## 🐳 Docker Deployment
Run the full stack (FastAPI Backend + Mosquitto MQTT Broker) with Docker Compose:
```bash
docker-compose up --build
```

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Server health check and version status |
| `GET` | `/api/v1/incidents` | List all active and recorded emergency incidents |
| `GET` | `/api/v1/incidents/{incident_id}` | Detailed telemetry stream, vitals, and drone track |
| `GET` | `/api/v1/incidents/{incident_id}/evidence-ledger` | Cryptographic evidence blocks and SHA-256 chain audit |
| `GET` | `/api/v1/drones/stations` | Cell tower drone base docks and status |
| `POST` | `/api/v1/sos/trigger` | Ingest edge telemetry packet or trigger manual SOS |
| `POST` | `/api/v1/drone/step` | Advance drone flight dynamics step |
| `WS` | `/ws/emergency-feed` | Real-time WebSocket telemetry stream for dispatch consoles |

---

## 🤝 Contributing
Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and review our open issues before submitting pull requests.

---

## 📜 License
Distributed under the **Apache License 2.0**. See [`LICENSE`](LICENSE) for more information.
