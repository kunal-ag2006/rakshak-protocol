"""Unit tests for Cryptographic Evidence Vault (SHA-256 Append-Only Ledger)."""

import unittest
import time
from server.app.evidence_vault import CryptographicEvidenceVault
from server.app.models import Coordinates, TelemetryFrame, ThreatSeverity


class TestEvidenceVault(unittest.TestCase):

    def setUp(self):
        self.vault = CryptographicEvidenceVault()

    def test_evidence_sealing_and_chain_verification(self):
        incident_id = "INC-TEST-EVIDENCE-01"

        frame1 = TelemetryFrame(
            incident_id=incident_id,
            user_id="USR-01",
            timestamp=1000.0,
            sequence_number=1,
            gps=Coordinates(latitude=28.6139, longitude=77.2090),
            heart_rate_bpm=160.0,
            hrv_rmssd=10.0,
            acoustic_category="SCREAM_DISTRESS",
            acoustic_confidence=0.9,
            threat_level=ThreatSeverity.CRITICAL,
            trigger_type="ZERO_CLICK_MFA"
        )
        block1 = self.vault.seal_frame(frame1)
        self.assertEqual(block1.block_index, 0)
        self.assertEqual(block1.previous_hash, CryptographicEvidenceVault.GENESIS_HASH)

        frame2 = TelemetryFrame(
            incident_id=incident_id,
            user_id="USR-01",
            timestamp=1001.0,
            sequence_number=2,
            gps=Coordinates(latitude=28.6140, longitude=77.2091),
            heart_rate_bpm=162.0,
            hrv_rmssd=9.5,
            acoustic_category="SCREAM_DISTRESS",
            acoustic_confidence=0.92,
            threat_level=ThreatSeverity.CRITICAL,
            trigger_type="ZERO_CLICK_MFA"
        )
        block2 = self.vault.seal_frame(frame2)
        self.assertEqual(block2.block_index, 1)
        self.assertEqual(block2.previous_hash, block1.current_hash)

        # Verify integrity
        is_valid, msg = self.vault.verify_chain_integrity(incident_id)
        self.assertTrue(is_valid)
        self.assertIn("Cryptographic integrity verified", msg)

    def test_tamper_detection(self):
        incident_id = "INC-TEST-TAMPER-02"
        frame = TelemetryFrame(
            incident_id=incident_id,
            user_id="USR-01",
            timestamp=1000.0,
            sequence_number=1,
            gps=Coordinates(latitude=28.6139, longitude=77.2090),
            heart_rate_bpm=160.0,
            hrv_rmssd=10.0,
            acoustic_category="SCREAM_DISTRESS",
            acoustic_confidence=0.9,
            threat_level=ThreatSeverity.CRITICAL,
            trigger_type="ZERO_CLICK_MFA"
        )
        block = self.vault.seal_frame(frame)

        # Tamper with internal data
        block.data["telemetry"]["heart_rate_bpm"] = 80.0 # Alter recorded HR

        is_valid, msg = self.vault.verify_chain_integrity(incident_id)
        self.assertFalse(is_valid)
        self.assertIn("tampering detected", msg)


if __name__ == "__main__":
    unittest.main()
