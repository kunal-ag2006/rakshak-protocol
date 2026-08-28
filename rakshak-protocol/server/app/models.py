"""Pydantic data schemas for Rakshak Protocol."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import time


def dump_model(obj: Any) -> Any:
    """Helper to dump pydantic models across v1 and v2."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        return obj.dict()
    return obj


class ThreatSeverity(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DISPATCHED = "DISPATCHED"
    DRONE_ON_SCENE = "DRONE_ON_SCENE"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class DroneStatus(str, Enum):
    DOCKED_READY = "DOCKED_READY"
    LAUNCHING = "LAUNCHING"
    TRANSIT_TO_TARGET = "TRANSIT_TO_TARGET"
    ON_SCENE_LOITERING = "ON_SCENE_LOITERING"
    RETURNING_TO_BASE = "RETURNING_TO_BASE"
    MAINTENANCE = "MAINTENANCE"


class Coordinates(BaseModel):
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    accuracy_m: float = 5.0
    speed_mps: float = 0.0
    heading_deg: float = 0.0


class TelemetryFrame(BaseModel):
    incident_id: str
    user_id: str
    timestamp: float = Field(default_factory=time.time)
    sequence_number: int
    gps: Coordinates
    heart_rate_bpm: float
    hrv_rmssd: float
    acoustic_category: str
    acoustic_confidence: float
    threat_level: ThreatSeverity = ThreatSeverity.CRITICAL
    trigger_type: str
    stealth_mode_active: bool = True
    battery_level_pct: float = 90.0
    payload_hmac: Optional[str] = None


class DroneStation(BaseModel):
    station_id: str
    name: str
    cell_tower_id: str
    location: Coordinates
    assigned_drone_id: str
    drone_status: DroneStatus = DroneStatus.DOCKED_READY
    drone_battery_pct: float = 100.0
    coverage_radius_km: float = 7.5


class DroneTelemetry(BaseModel):
    drone_id: str
    station_id: str
    incident_id: Optional[str] = None
    status: DroneStatus
    current_location: Coordinates
    target_location: Optional[Coordinates] = None
    battery_pct: float
    speed_mps: float
    altitude_agl_m: float
    distance_to_target_m: float
    eta_seconds: float
    spotlight_active: bool = False
    siren_active: bool = False
    camera_locked: bool = False
    timestamp: float = Field(default_factory=time.time)


class EvidenceBlock(BaseModel):
    block_index: int
    incident_id: str
    timestamp: float
    previous_hash: str
    telemetry_hash: str
    data: Dict[str, Any]
    current_hash: str


class IncidentSummary(BaseModel):
    incident_id: str
    user_id: str
    status: IncidentStatus
    threat_level: ThreatSeverity
    trigger_type: str
    created_at: float
    last_update: float
    initial_location: Coordinates
    latest_location: Coordinates
    latest_hr_bpm: float
    latest_hrv_rmssd: float
    acoustic_event: str
    assigned_drone_id: Optional[str] = None
    drone_eta_seconds: Optional[float] = None
    evidence_block_count: int = 0
    chain_verified: bool = True
