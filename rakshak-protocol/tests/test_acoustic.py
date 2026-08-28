"""Unit tests for TinyML Acoustic Threat Classifier."""

import unittest
import numpy as np
from edge_device.acoustic_engine import AcousticThreatCategory, TinyMLAcousticEngine
from simulations.mock_data import generate_audio_pcm


class TestAcousticEngine(unittest.TestCase):

    def setUp(self):
        self.engine = TinyMLAcousticEngine(sample_rate=16000, confidence_threshold=0.70)

    def test_ambient_audio_classification(self):
        audio = generate_audio_pcm("ambient", duration_sec=1.0)
        res = self.engine.classify_frame(audio)
        self.assertFalse(res.is_threat)
        self.assertEqual(res.category, AcousticThreatCategory.AMBIENT_NORMAL)

    def test_gunshot_classification(self):
        audio = generate_audio_pcm("gunshot", duration_sec=1.0)
        res = self.engine.classify_frame(audio)
        self.assertTrue(res.is_threat)
        self.assertEqual(res.category, AcousticThreatCategory.GUNSHOT_EXPLOSION)
        self.assertGreaterEqual(res.confidence, 0.85)

    def test_scream_classification(self):
        audio = generate_audio_pcm("scream", duration_sec=1.0)
        res = self.engine.classify_frame(audio)
        self.assertTrue(res.is_threat)
        self.assertIn(res.category, [AcousticThreatCategory.SCREAM_DISTRESS, AcousticThreatCategory.GUNSHOT_EXPLOSION])

    def test_panic_keyword_override(self):
        audio = generate_audio_pcm("ambient", duration_sec=1.0)
        res = self.engine.classify_frame(audio, explicit_keyword="Bachao")
        self.assertTrue(res.is_threat)
        self.assertEqual(res.category, AcousticThreatCategory.PANIC_KEYWORD)


if __name__ == "__main__":
    unittest.main()
