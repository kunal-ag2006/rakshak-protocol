"""
Autonomous Drone Routing & Cell-Tower Station Allocation Engine.
Calculates geospatial distance (Haversine), allocates nearest cell tower dock,
and generates MAVLink/REST navigation commands with sub-3-minute arrival optimization.
"""

import math
import time
from typing import Dict, List, Optional, Tuple
from server.app.models import Coordinates, DroneStation, DroneStatus, DroneTelemetry


def haversine_distance_meters(c1: Coordinates, c2: Coordinates) -> float:
    """Calculate Great Circle distance between two GPS coordinates in meters."""
    R = 6371000.0  # Earth radius in meters
    lat1_rad = math.radians(c1.latitude)
    lat2_rad = math.radians(c2.latitude)
    dlat = math.radians(c2.latitude - c1.latitude)
    dlon = math.radians(c2.longitude - c1.longitude)

    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_bearing_degrees(c1: Coordinates, c2: Coordinates) -> float:
    """Calculate initial compass bearing from c1 to c2."""
    lat1 = math.radians(c1.latitude)
    lat2 = math.radians(c2.latitude)
    dlon = math.radians(c2.longitude - c1.longitude)

    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0


class DroneRouter:
    """
    Dispatches and tracks autonomous police drones stationed at urban cell towers.
    """

    def __init__(self, cruise_speed_mps: float = 22.2):
        self.cruise_speed_mps = cruise_speed_mps  # ~80 km/h
        self.stations: Dict[str, DroneStation] = {}
        self.drones_telemetry: Dict[str, DroneTelemetry] = {}
        self._init_default_stations()

    def _init_default_stations(self):
        """Initialize mock cell-tower docking stations across Delhi NCR / Urban grid."""
        default_stations = [
            DroneStation(
                station_id="STATION-TOWER-01",
                name="Airtel Tower #402 (Connaught Place)",
                cell_tower_id="CELL-DEL-CP-01",
                location=Coordinates(latitude=28.6315, longitude=77.2167, altitude_m=45.0),
                assigned_drone_id="DRONE-RAKSHAK-01",
                drone_status=DroneStatus.DOCKED_READY,
                drone_battery_pct=100.0,
                coverage_radius_km=6.0,
            ),
            DroneStation(
                station_id="STATION-TOWER-02",
                name="Jio 5G Tower #118 (Hauz Khas)",
                cell_tower_id="CELL-DEL-HK-02",
                location=Coordinates(latitude=28.5494, longitude=77.2001, altitude_m=50.0),
                assigned_drone_id="DRONE-RAKSHAK-02",
                drone_status=DroneStatus.DOCKED_READY,
                drone_battery_pct=96.0,
                coverage_radius_km=7.0,
            ),
            DroneStation(
                station_id="STATION-TOWER-03",
                name="BSNL Civic Tower #089 (Dwarka Sector 12)",
                cell_tower_id="CELL-DEL-DW-03",
                location=Coordinates(latitude=28.5921, longitude=77.0460, altitude_m=40.0),
                assigned_drone_id="DRONE-RAKSHAK-03",
                drone_status=DroneStatus.DOCKED_READY,
                drone_battery_pct=100.0,
                coverage_radius_km=8.0,
            ),
            DroneStation(
                station_id="STATION-TOWER-04",
                name="Airtel 5G Tower #304 (Cyber City, Gurugram)",
                cell_tower_id="CELL-GGN-CC-04",
                location=Coordinates(latitude=28.4950, longitude=77.0895, altitude_m=60.0),
                assigned_drone_id="DRONE-RAKSHAK-04",
                drone_status=DroneStatus.DOCKED_READY,
                drone_battery_pct=98.0,
                coverage_radius_km=7.5,
            ),
        ]
        for s in default_stations:
            self.stations[s.station_id] = s
            self.drones_telemetry[s.assigned_drone_id] = DroneTelemetry(
                drone_id=s.assigned_drone_id,
                station_id=s.station_id,
                status=DroneStatus.DOCKED_READY,
                current_location=s.location,
                battery_pct=s.drone_battery_pct,
                speed_mps=0.0,
                altitude_agl_m=0.0,
                distance_to_target_m=0.0,
                eta_seconds=0.0,
            )

    def find_nearest_ready_station(self, target: Coordinates) -> Optional[Tuple[DroneStation, float, float]]:
        """
        Find closest cell-tower station with an available, charged drone.
        Returns (Station, distance_in_meters, eta_in_seconds).
        """
        best_station: Optional[DroneStation] = None
        min_dist = float("inf")

        for station in self.stations.values():
            if station.drone_status == DroneStatus.DOCKED_READY and station.drone_battery_pct >= 30.0:
                dist = haversine_distance_meters(station.location, target)
                if dist < min_dist:
                    min_dist = dist
                    best_station = station

        if not best_station:
            return None

        # ETA = (Launch time ~10s) + (distance / cruise_speed)
        eta_seconds = 10.0 + (min_dist / self.cruise_speed_mps)
        return best_station, min_dist, eta_seconds

    def dispatch_drone(self, incident_id: str, target: Coordinates) -> Optional[DroneTelemetry]:
        """Deploy nearest drone to target coordinates."""
        match = self.find_nearest_ready_station(target)
        if not match:
            return None

        station, distance_m, eta_s = match
        drone_id = station.assigned_drone_id

        # Update station and drone status
        station.drone_status = DroneStatus.LAUNCHING
        telemetry = DroneTelemetry(
            drone_id=drone_id,
            station_id=station.station_id,
            incident_id=incident_id,
            status=DroneStatus.TRANSIT_TO_TARGET,
            current_location=station.location,
            target_location=target,
            battery_pct=station.drone_battery_pct,
            speed_mps=self.cruise_speed_mps,
            altitude_agl_m=65.0,  # Urban safe flight altitude
            distance_to_target_m=distance_m,
            eta_seconds=eta_s,
            spotlight_active=True,   # Deterrent lighting activated
            siren_active=True,       # Audio warning beacon activated
            camera_locked=True,      # Thermal/Optical gimbal locked on victim GPS
        )

        self.drones_telemetry[drone_id] = telemetry
        return telemetry

    def simulate_drone_step(self, drone_id: str, dt_seconds: float = 1.0) -> Optional[DroneTelemetry]:
        """Simulate drone flight progress towards target."""
        t = self.drones_telemetry.get(drone_id)
        if not t or not t.target_location or t.status not in [DroneStatus.TRANSIT_TO_TARGET, DroneStatus.ON_SCENE_LOITERING]:
            return t

        if t.status == DroneStatus.TRANSIT_TO_TARGET:
            curr_dist = haversine_distance_meters(t.current_location, t.target_location)
            step_dist = t.speed_mps * dt_seconds

            if curr_dist <= step_dist or curr_dist < 15.0:
                # Arrived on scene!
                t.current_location = t.target_location
                t.status = DroneStatus.ON_SCENE_LOITERING
                t.speed_mps = 0.0
                t.distance_to_target_m = 0.0
                t.eta_seconds = 0.0
                t.altitude_agl_m = 30.0  # Lower altitude for tactical deterrence & visual recording
            else:
                # Interpolate towards target
                fraction = step_dist / curr_dist
                new_lat = t.current_location.latitude + (t.target_location.latitude - t.current_location.latitude) * fraction
                new_lon = t.current_location.longitude + (t.target_location.longitude - t.current_location.longitude) * fraction
                t.current_location = Coordinates(latitude=new_lat, longitude=new_lon, altitude_m=t.altitude_agl_m)
                t.distance_to_target_m = curr_dist - step_dist
                t.eta_seconds = max(0.0, t.distance_to_target_m / t.speed_mps)

            # Battery drain simulation
            t.battery_pct = max(5.0, t.battery_pct - 0.05 * dt_seconds)

        t.timestamp = time.time()
        return t


# Singleton instance
drone_router = DroneRouter()
