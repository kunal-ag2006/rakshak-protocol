"""Unit tests for Drone Router & Cell-Tower Allocation."""

import unittest
from server.app.drone_router import Coordinates, DroneRouter, DroneStatus, haversine_distance_meters


class TestDroneRouter(unittest.TestCase):

    def setUp(self):
        self.router = DroneRouter(cruise_speed_mps=22.2)

    def test_haversine_distance(self):
        # Distance between Connaught Place (28.6315, 77.2167) and India Gate (28.6129, 77.2295) is ~2.4 km
        c1 = Coordinates(latitude=28.6315, longitude=77.2167)
        c2 = Coordinates(latitude=28.6129, longitude=77.2295)
        dist = haversine_distance_meters(c1, c2)
        self.assertGreater(dist, 2000.0)
        self.assertLess(dist, 3000.0)

    def test_nearest_drone_station_allocation_and_dispatch(self):
        target = Coordinates(latitude=28.6300, longitude=77.2150) # Near Connaught Place Tower 01
        telemetry = self.router.dispatch_drone("INC-TEST-01", target)
        self.assertIsNotNone(telemetry)
        self.assertEqual(telemetry.drone_id, "DRONE-RAKSHAK-01")
        self.assertEqual(telemetry.status, DroneStatus.TRANSIT_TO_TARGET)
        self.assertTrue(telemetry.spotlight_active)
        self.assertTrue(telemetry.siren_active)
        self.assertLess(telemetry.eta_seconds, 120.0) # Sub-2-minute response

    def test_drone_flight_step_to_arrival(self):
        target = Coordinates(latitude=28.6320, longitude=77.2170)
        self.router.dispatch_drone("INC-TEST-02", target)
        # Advance flight simulation by 100 seconds
        updated = self.router.simulate_drone_step("DRONE-RAKSHAK-01", dt_seconds=100.0)
        self.assertEqual(updated.status, DroneStatus.ON_SCENE_LOITERING)
        self.assertEqual(updated.altitude_agl_m, 30.0)


if __name__ == "__main__":
    unittest.main()
