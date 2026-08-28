"""
MQTT Broker Integration & Incident Coordinator for Rakshak Protocol.
Ingests real-time SOS streams, writes to cryptographic evidence vault,
and automatically triggers autonomous drone dispatch.
"""

import asyncio
from dataclasses import asdict
import time
from typing import Any, Callable, Dict, List, Optional
from server.app.evidence_vault import evidence_vault
from server.app.drone_router import drone_router
from server.app.models import (
    Coordinates,
    DroneTelemetry,
    IncidentStatus,
    IncidentSummary,
    TelemetryFrame,
    ThreatSeverity,
    dump_model,
)


class IncidentManager:
    """
    Tracks and coordinates active and historical emergency incidents.
    """

    def __init__(self):
        self.active_incidents: Dict[str, IncidentSummary] = {}
        self.telemetry_history: Dict[str, List[TelemetryFrame]] = {}
        self.subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def register_broadcast_listener(self, listener: Callable[[Dict[str, Any]], None]):
        self.subscribers.append(listener)

    def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        payload = {"event": event_type, "data": data, "timestamp": time.time()}
        for sub in self.subscribers:
            try:
                sub(payload)
            except Exception as e:
                print(f"[IncidentManager] Broadcast error: {e}")

    def ingest_telemetry_frame(self, frame: TelemetryFrame) -> Dict[str, Any]:
        """
        Process incoming telemetry packet:
        1. Seal into append-only cryptographic ledger.
        2. Create or update incident.
        3. Dispatch autonomous drone if not already deployed.
        4. Broadcast live telemetry to dispatch center.
        """
        incident_id = frame.incident_id

        # 1. Append to Evidence Vault (SHA-256 Chain)
        evidence_block = evidence_vault.seal_frame(frame)

        # Store in history
        if incident_id not in self.telemetry_history:
            self.telemetry_history[incident_id] = []
        self.telemetry_history[incident_id].append(frame)

        # 2. Check or Create Incident
        now = time.time()
        is_new_incident = incident_id not in self.active_incidents
        assigned_drone: Optional[DroneTelemetry] = None

        if is_new_incident:
            # Automatic Drone Dispatch
            assigned_drone = drone_router.dispatch_drone(incident_id, frame.gps)
            drone_id = assigned_drone.drone_id if assigned_drone else None
            eta = assigned_drone.eta_seconds if assigned_drone else None

            incident = IncidentSummary(
                incident_id=incident_id,
                user_id=frame.user_id,
                status=IncidentStatus.DISPATCHED if assigned_drone else IncidentStatus.ACTIVE,
                threat_level=frame.threat_level,
                trigger_type=frame.trigger_type,
                created_at=now,
                last_update=now,
                initial_location=frame.gps,
                latest_location=frame.gps,
                latest_hr_bpm=frame.heart_rate_bpm,
                latest_hrv_rmssd=frame.hrv_rmssd,
                acoustic_event=frame.acoustic_category,
                assigned_drone_id=drone_id,
                drone_eta_seconds=eta,
                evidence_block_count=1,
                chain_verified=True,
            )
            self.active_incidents[incident_id] = incident

            self.broadcast_event("NEW_INCIDENT_SOS", {
                "incident": dump_model(incident),
                "evidence_block": dump_model(evidence_block),
                "drone": dump_model(assigned_drone) if assigned_drone else None
            })
        else:
            incident = self.active_incidents[incident_id]
            incident.last_update = now
            incident.latest_location = frame.gps
            incident.latest_hr_bpm = frame.heart_rate_bpm
            incident.latest_hrv_rmssd = frame.hrv_rmssd
            incident.acoustic_event = frame.acoustic_category
            incident.evidence_block_count = len(evidence_vault.get_chain(incident_id))

            # Update drone ETA if drone is assigned
            if incident.assigned_drone_id and incident.assigned_drone_id in drone_router.drones_telemetry:
                d_telemetry = drone_router.drones_telemetry[incident.assigned_drone_id]
                incident.drone_eta_seconds = d_telemetry.eta_seconds

            self.broadcast_event("TELEMETRY_UPDATE", {
                "incident_id": incident_id,
                "telemetry": dump_model(frame),
                "evidence_block_hash": evidence_block.current_hash,
                "block_index": evidence_block.block_index,
            })

        return {
            "status": "INGESTED",
            "incident_id": incident_id,
            "block_index": evidence_block.block_index,
            "block_hash": evidence_block.current_hash,
            "assigned_drone_id": incident.assigned_drone_id if not is_new_incident else (assigned_drone.drone_id if assigned_drone else None)
        }


# Singleton instance
incident_manager = IncidentManager()
