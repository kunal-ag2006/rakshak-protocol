"""Unit tests for Stealth SOS Controller & Multi-Factor State Machine."""

import unittest
import numpy as np
from edge_device.stealth_controller import StealthSOSController, SystemState
from edge_device.hardware_interrupt import HardwareInterruptListener
from simulations.mock_data import generate_audio_pcm, generate_vitals_scenario


class TestStealthSOSController(unittest.TestCase):

    def setUp(self):
        self.hw_listener = HardwareInterruptListener(long_press_threshold_sec=3.0)
        self.controller = StealthSOSController(
            user_id="USR-TEST-001",
            hardware_listener=self.hw_listener
        )

    def test_multi_factor_threat_triggers_stealth_sos(self):
        vitals_panic = generate_vitals_scenario("acute_panic_attack_assault")
        audio_gunshot = generate_audio_pcm("gunshot", duration_sec=1.0)

        res = self.controller.process_tick(vitals_panic, audio_gunshot)
        self.assertTrue(res.is_sos_triggered)
        self.assertEqual(res.system_state, SystemState.STEALTH_SOS_ACTIVE)
        self.assertTrue(res.stealth_display_blackout)
        self.assertTrue(res.stealth_audio_streaming)
        self.assertIsNotNone(res.incident_id)

    def test_hardware_interrupt_override(self):
        # Simulate 3.2 second hardware power key hold
        self.hw_listener.trigger_button_down("POWER_KEY", timestamp=100.0)
        self.hw_listener.trigger_button_up("POWER_KEY", timestamp=103.2)

        vitals_normal = generate_vitals_scenario("nominal_resting")
        audio_normal = generate_audio_pcm("ambient", duration_sec=1.0)

        res = self.controller.process_tick(vitals_normal, audio_normal)
        self.assertTrue(res.is_sos_triggered)
        self.assertEqual(res.trigger_type, "HARDWARE_INTERRUPT_OVERRIDE")
        self.assertEqual(res.system_state, SystemState.STEALTH_SOS_ACTIVE)


if __name__ == "__main__":
    unittest.main()
