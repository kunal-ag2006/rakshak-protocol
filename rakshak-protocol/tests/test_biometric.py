"""Unit tests for Biometric Triage Engine."""

import unittest
import numpy as np
from edge_device.biometric_engine import BiometricTriageEngine, BiometricVitals


class TestBiometricTriageEngine(unittest.TestCase):

    def setUp(self):
        self.engine = BiometricTriageEngine(
            hr_panic_threshold=150.0,
            hr_spike_delta_threshold=40.0,
            hrv_rmssd_critical_low=18.0,
            hrv_sdnn_critical_low=25.0
        )
        self.engine.set_baseline(70.0)

    def test_nominal_resting_vitals(self):
        vitals = BiometricVitals(
            timestamp=1000.0,
            heart_rate_bpm=72.0,
            rr_intervals_ms=[820.0, 840.0, 810.0, 850.0, 830.0, 825.0],
            accelerometer_magnitude=1.0
        )
        res = self.engine.evaluate_vitals(vitals)
        self.assertFalse(res.is_threat)
        self.assertLess(res.threat_score, 0.4)
        self.assertGreater(res.hrv_rmssd, 18.0)

    def test_acute_tachycardia_and_hrv_collapse(self):
        # Panic / terror: HR > 150 BPM and RMSSD < 18ms
        vitals = BiometricVitals(
            timestamp=1001.0,
            heart_rate_bpm=165.0,
            rr_intervals_ms=[363.0, 364.0, 363.5, 364.2, 363.8, 364.0],
            accelerometer_magnitude=1.2
        )
        res = self.engine.evaluate_vitals(vitals)
        self.assertTrue(res.is_threat)
        self.assertGreaterEqual(res.threat_score, 0.7)
        self.assertLess(res.hrv_rmssd, 18.0)

    def test_exercise_false_positive_damping(self):
        # Jogging: HR 140 BPM with high motion and preserved HRV variability
        vitals = BiometricVitals(
            timestamp=1002.0,
            heart_rate_bpm=138.0,
            rr_intervals_ms=[410.0, 450.0, 420.0, 460.0, 430.0],
            accelerometer_magnitude=4.5
        )
        res = self.engine.evaluate_vitals(vitals)
        self.assertFalse(res.is_threat)


if __name__ == "__main__":
    unittest.main()
