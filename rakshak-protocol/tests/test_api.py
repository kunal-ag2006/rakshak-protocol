"""Integration tests for FastAPI REST Endpoints."""

import unittest
from fastapi.testclient import TestClient
from server.app.main import app
from server.app.models import Coordinates, TelemetryFrame, ThreatSeverity


class TestFastAPIEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "HEALTHY")

    def test_list_drone_stations(self):
        response = self.client.get("/api/v1/drones/stations")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("stations", data)
        self.assertGreaterEqual(len(data["stations"]), 1)

    def test_sos_trigger_and_ledger_lookup(self):
        incident_id = "INC-API-TEST-01"
        payload = {
            "incident_id": incident_id,
            "user_id": "USR-API-USER",
            "sequence_number": 1,
            "gps": {"latitude": 28.6139, "longitude": 77.2090, "altitude_m": 15.0},
            "heart_rate_bpm": 165.0,
            "hrv_rmssd": 10.2,
            "acoustic_category": "SCREAM_DISTRESS",
            "acoustic_confidence": 0.95,
            "threat_level": "CRITICAL",
            "trigger_type": "ZERO_CLICK_MFA",
            "stealth_mode_active": True,
            "battery_level_pct": 89.0
        }

        # 1. Trigger SOS
        post_res = self.client.post("/api/v1/sos/trigger", json=payload)
        self.assertEqual(post_res.status_code, 200)
        post_data = post_res.json()
        self.assertEqual(post_data["status"], "INGESTED")
        self.assertEqual(post_data["incident_id"], incident_id)

        # 2. Check Incident Details
        inc_res = self.client.get(f"/api/v1/incidents/{incident_id}")
        self.assertEqual(inc_res.status_code, 200)
        inc_data = inc_res.json()
        self.assertEqual(inc_data["incident"]["incident_id"], incident_id)
        self.assertTrue(inc_data["evidence_integrity_verified"])

        # 3. Check Evidence Ledger
        ledger_res = self.client.get(f"/api/v1/incidents/{incident_id}/evidence-ledger")
        self.assertEqual(ledger_res.status_code, 200)
        ledger_data = ledger_res.json()
        self.assertTrue(ledger_data["chain_integrity_valid"])
        self.assertGreaterEqual(ledger_data["block_count"], 1)


if __name__ == "__main__":
    unittest.main()
