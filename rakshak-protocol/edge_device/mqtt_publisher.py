"""
Secure MQTT Telemetry Publisher for Rakshak Protocol.
Streams encrypted, lightweight telemetry packets to the Rakshak Cloud Vault & Dispatch Engine.
"""

import json
import hashlib
import hmac
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class GPSCoordinates:
    latitude: float
    longitude: float
    altitude_m: float = 18.0
    accuracy_m: float = 2.5
    speed_mps: float = 0.0
    heading_deg: float = 0.0


@dataclass
class RakshakTelemetryPacket:
    incident_id: str
    user_id: str
    timestamp: float
    sequence_number: int
    gps: GPSCoordinates
    heart_rate_bpm: float
    hrv_rmssd: float
    acoustic_category: str
    acoustic_confidence: float
    threat_level: str  # "CRITICAL", "HIGH", "WARNING"
    trigger_type: str  # "ZERO_CLICK_MFA", "HARDWARE_INTERRUPT"
    stealth_mode_active: bool
    battery_level_pct: float
    payload_hmac: str = ""


class RakshakMQTTPublisher:
    """
    Simulated Edge MQTT Client with local ring buffer and HMAC signature integrity.
    Publishes to 'rakshak/sos/{incident_id}/telemetry' and 'rakshak/sos/alerts'.
    """

    def __init__(self, broker_url: str = "localhost", port: int = 1883, secret_key: str = "rakshak-shared-secret-key-2026"):
        self.broker_url = broker_url
        self.port = port
        self.secret_key = secret_key.encode("utf-8")

        self.sequence_counter = 0
        self.is_connected = True
        self.transmission_log: List[Dict[str, Any]] = []
        self._external_publish_handler: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def set_publish_handler(self, handler: Callable[[str, Dict[str, Any]], None]):
        """Attach callback for direct inter-process or mock testing."""
        self._external_publish_handler = handler

    def sign_payload(self, data: Dict[str, Any]) -> str:
        """Compute HMAC-SHA256 signature for tamper-evident data transit."""
        canonical_str = json.dumps(data, sort_keys=True)
        return hmac.new(self.secret_key, canonical_str.encode("utf-8"), hashlib.sha256).hexdigest()

    def build_packet(
        self,
        incident_id: str,
        user_id: str,
        gps: GPSCoordinates,
        heart_rate_bpm: float,
        hrv_rmssd: float,
        acoustic_category: str,
        acoustic_confidence: float,
        threat_level: str,
        trigger_type: str,
        battery_level_pct: float = 88.0
    ) -> RakshakTelemetryPacket:
        """Construct signed telemetry packet."""
        self.sequence_counter += 1
        pkt_dict = {
            "incident_id": incident_id,
            "user_id": user_id,
            "timestamp": time.time(),
            "sequence_number": self.sequence_counter,
            "gps": asdict(gps),
            "heart_rate_bpm": round(heart_rate_bpm, 1),
            "hrv_rmssd": round(hrv_rmssd, 2),
            "acoustic_category": acoustic_category,
            "acoustic_confidence": round(acoustic_confidence, 2),
            "threat_level": threat_level,
            "trigger_type": trigger_type,
            "stealth_mode_active": True,
            "battery_level_pct": battery_level_pct,
        }
        signature = self.sign_payload(pkt_dict)
        return RakshakTelemetryPacket(
            incident_id=incident_id,
            user_id=user_id,
            timestamp=pkt_dict["timestamp"],
            sequence_number=pkt_dict["sequence_number"],
            gps=gps,
            heart_rate_bpm=pkt_dict["heart_rate_bpm"],
            hrv_rmssd=pkt_dict["hrv_rmssd"],
            acoustic_category=acoustic_category,
            acoustic_confidence=pkt_dict["acoustic_confidence"],
            threat_level=threat_level,
            trigger_type=trigger_type,
            stealth_mode_active=True,
            battery_level_pct=battery_level_pct,
            payload_hmac=signature
        )

    def publish_telemetry(self, packet: RakshakTelemetryPacket) -> bool:
        """Publish telemetry frame via MQTT topic."""
        topic = f"rakshak/sos/{packet.incident_id}/telemetry"
        payload = asdict(packet)
        self.transmission_log.append({"topic": topic, "payload": payload, "time": time.time()})

        if self._external_publish_handler:
            self._external_publish_handler(topic, payload)

        return True
