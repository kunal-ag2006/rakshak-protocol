# Rakshak Protocol - Telemetry & MQTT Specification

## 1. MQTT Topic Hierarchy
```
rakshak/
├── sos/
│   ├── alerts                          # Global incident notification stream (QoS 2)
│   └── {incident_id}/
│       ├── telemetry                   # Edge device GPS, Biometrics, Acoustic metadata (QoS 1)
│       └── audio_stream                # Compressed Opus audio buffers (QoS 1)
├── drone/
│   ├── {drone_id}/
│   │   ├── telemetry                   # Drone GPS, altitude, battery, heading (QoS 1)
│   │   └── commands                    # MAVLink navigation, payload trigger (QoS 2)
└── vault/
    └── {incident_id}/audit             # Cryptographic block creation notices
```

---

## 2. Telemetry Packet Schema (`TelemetryFrame`)
```json
{
  "incident_id": "INC-AA40D7E1",
  "user_id": "USR-PRIYA-SHARMA-01",
  "timestamp": 1787906315.316,
  "sequence_number": 1,
  "gps": {
    "latitude": 28.6289,
    "longitude": 77.2065,
    "altitude_m": 16.0,
    "accuracy_m": 2.5,
    "speed_mps": 0.0,
    "heading_deg": 0.0
  },
  "heart_rate_bpm": 166.0,
  "hrv_rmssd": 3.0,
  "acoustic_category": "SCREAM_DISTRESS",
  "acoustic_confidence": 0.94,
  "threat_level": "CRITICAL",
  "trigger_type": "ZERO_CLICK_MULTI_FACTOR_DANGER",
  "stealth_mode_active": true,
  "battery_level_pct": 92.0,
  "payload_hmac": "4b85aba6c2425319e782a934bb..."
}
```

---

## 3. HMAC Message Authentication
Each edge client holds a pre-shared symmetrical key or device-specific certificate. The HMAC signature covers all canonical JSON fields sorted alphabetically:

$$\text{Signature} = \text{HMAC-SHA256}(K_{\text{secret}}, \text{CanonicalJSON}(\text{Payload}))$$
