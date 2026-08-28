"""
Autonomous Police Drone Flight & Deterrence Simulator.
Simulates MAVLink telemetry, rapid waypoint navigation from cell towers,
high-intensity visual strobe deployment, and live optical/thermal sensor tracking.
"""

from dataclasses import dataclass
from enum import Enum
import math
import time
from typing import Callable, Dict, List, Optional
from server.app.models import Coordinates, DroneStatus, DroneTelemetry


class DroneFlightSimulator:
    """
    Simulates rapid response autonomous police drone stationed on cell towers.
    """

    def __init__(
        self,
        drone_id: str,
        home_tower_id: str,
        home_location: Coordinates,
        cruise_speed_mps: float = 22.2,  # 80 km/h
        max_altitude_m: float = 65.0,
    ):
        self.drone_id = drone_id
        self.home_tower_id = home_tower_id
        self.home_location = home_location
        self.cruise_speed_mps = cruise_speed_mps
        self.max_altitude_m = max_altitude_m

        self.current_location = Coordinates(
            latitude=home_location.latitude,
            longitude=home_location.longitude,
            altitude_m=0.0
        )
        self.status = DroneStatus.DOCKED_READY
        self.target_location: Optional[Coordinates] = None
        self.active_incident_id: Optional[str] = None
        self.battery_pct: float = 100.0

        self.spotlight_active: bool = False
        self.siren_active: bool = False
        self.camera_gimbal_locked: bool = False

    def deploy_to_target(self, incident_id: str, target: Coordinates) -> DroneTelemetry:
        """Launch drone towards victim's live GPS coordinates."""
        self.active_incident_id = incident_id
        self.target_location = target
        self.status = DroneStatus.TRANSIT_TO_TARGET
        self.spotlight_active = True
        self.siren_active = True
        self.camera_gimbal_locked = True
        return self.get_telemetry()

    def step_simulation(self, dt_seconds: float = 1.0) -> DroneTelemetry:
        """Advance physical flight dynamics by dt_seconds."""
        if self.status == DroneStatus.TRANSIT_TO_TARGET and self.target_location:
            # Fly towards target
            lat_diff = self.target_location.latitude - self.current_location.latitude
            lon_diff = self.target_location.longitude - self.current_location.longitude
            dist_deg = math.hypot(lat_diff, lon_diff)

            # Approx 1 deg lat = 111,000 meters
            dist_m = dist_deg * 111000.0
            step_m = self.cruise_speed_mps * dt_seconds

            if dist_m <= step_m or dist_m < 10.0:
                # Target reached
                self.current_location = Coordinates(
                    latitude=self.target_location.latitude,
                    longitude=self.target_location.longitude,
                    altitude_m=30.0
                )
                self.status = DroneStatus.ON_SCENE_LOITERING
            else:
                fraction = step_m / dist_m
                new_lat = self.current_location.latitude + lat_diff * fraction
                new_lon = self.current_location.longitude + lon_diff * fraction
                self.current_location = Coordinates(
                    latitude=new_lat,
                    longitude=new_lon,
                    altitude_m=self.max_altitude_m
                )

            self.battery_pct = max(5.0, self.battery_pct - 0.04 * dt_seconds)

        elif self.status == DroneStatus.ON_SCENE_LOITERING:
            self.battery_pct = max(5.0, self.battery_pct - 0.03 * dt_seconds)

        return self.get_telemetry()

    def get_telemetry(self) -> DroneTelemetry:
        dist_m = 0.0
        eta_s = 0.0
        if self.target_location:
            lat_diff = self.target_location.latitude - self.current_location.latitude
            lon_diff = self.target_location.longitude - self.current_location.longitude
            dist_m = math.hypot(lat_diff, lon_diff) * 111000.0
            eta_s = dist_m / self.cruise_speed_mps if self.cruise_speed_mps > 0 else 0.0

        return DroneTelemetry(
            drone_id=self.drone_id,
            station_id=self.home_tower_id,
            incident_id=self.active_incident_id,
            status=self.status,
            current_location=self.current_location,
            target_location=self.target_location,
            battery_pct=round(self.battery_pct, 1),
            speed_mps=self.cruise_speed_mps if self.status == DroneStatus.TRANSIT_TO_TARGET else 0.0,
            altitude_agl_m=self.current_location.altitude_m,
            distance_to_target_m=round(dist_m, 1),
            eta_seconds=round(eta_s, 1),
            spotlight_active=self.spotlight_active,
            siren_active=self.siren_active,
            camera_locked=self.camera_gimbal_locked,
            timestamp=time.time()
        )
