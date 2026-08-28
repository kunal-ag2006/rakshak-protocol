# Rakshak Protocol System Architecture

## 1. Overview
The **Rakshak Protocol** (Module 3 of the *TransparentGov* Civic Operating System) is an autonomous, life-saving emergency response framework designed for critical situations where victims are incapacitated, kidnapped, or unable to unlock their mobile phones.

By fusing **Edge TinyML Acoustic AI**, **Wearable Biometric Triage (PPG/HRV)**, **OS-Level Hardware Interrupts**, and **Autonomous Cell-Tower Drone Dispatch**, the system eliminates human delay and discretion in life-threatening scenarios.

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

## 2. Multi-Factor Threat Evaluation Logic (MFA for Danger)
Traditional SOS systems suffer from high false-alarm rates or require explicit user dexterity (unlocking the screen, dialing 112/911). Rakshak Protocol introduces Multi-Factor Danger Verification:

$$\text{SOS\_Trigger} = (\text{Condition}_A \land \text{Condition}_B) \lor \text{Condition}_C$$

Where:
- **$\text{Condition}_A$ (Biometric Triage):**
  - Instantaneous Heart Rate ($\text{HR} \ge 150 \text{ BPM}$) or Acute Surge ($\Delta \text{HR} \ge +40 \text{ BPM}$ above baseline).
  - Autonomic nervous collapse indicated by **$\text{RMSSD} \le 18 \text{ ms}$**.
  - Motion artifact filtering: damped if accelerometer indicates sustained cadence without acoustic distress.
- **$\text{Condition}_B$ (TinyML Acoustic Anomaly):**
  - High-frequency harmonic screaming (Spectral Centroid $> 1800 \text{ Hz}$, Roll-off $> 3000 \text{ Hz}$).
  - Impulsive blast/gunshot profiles (Peak amplitude $> 0.80$, Crest factor $> 5.5$).
  - High-frequency brittle impact (Glass shatter, ZCR $> 0.20$, Centroid $> 3500 \text{ Hz}$).
  - Keyword recognition ("Bachao", "Help me", "Save me").
- **$\text{Condition}_C$ (Hardware Interrupt):**
  - Physical button long-press ($\ge 3.0 \text{ seconds}$) on power or side key to allow manual override when hands are restrained.

---

## 3. Cryptographic Evidence Vault
Evidence tampering in law enforcement proceedings is mathematically prevented through an append-only SHA-256 hash chain:

$$H_0 = \text{Genesis}$$
$$H_i = \text{SHA256}\Big( i \parallel \text{IncidentID} \parallel T_i \parallel H_{i-1} \parallel \text{SHA256}(\text{Telemetry}_i) \parallel \text{SHA256}(\text{AudioChunk}_i) \Big)$$

Any unauthorized modification of sensor logs, GPS coordinates, or vitals invalidates all subsequent block hashes, providing undeniable judicial proof in court.
