"""
TinyML Acoustic Threat Detection Engine for Rakshak Protocol.
Performs real-time edge audio feature extraction and inference
to detect gunshots, distress screaming, glass breaking, and violent struggle.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np


class AcousticThreatCategory(str, Enum):
    AMBIENT_NORMAL = "AMBIENT_NORMAL"
    NORMAL_CONVERSATION = "NORMAL_CONVERSATION"
    SCREAM_DISTRESS = "SCREAM_DISTRESS"
    GUNSHOT_EXPLOSION = "GUNSHOT_EXPLOSION"
    GLASS_BREAK = "GLASS_BREAK"
    PANIC_KEYWORD = "PANIC_KEYWORD"
    VIOLENT_STRUGGLE = "VIOLENT_STRUGGLE"


@dataclass
class AudioFeatures:
    rms_energy: float
    zero_crossing_rate: float
    spectral_centroid_hz: float
    spectral_rolloff_hz: float
    spectral_flatness: float
    peak_amplitude: float
    crest_factor: float


@dataclass
class AcousticThreatAssessment:
    is_threat: bool
    category: AcousticThreatCategory
    confidence: float  # 0.0 to 1.0
    threat_score: float  # 0.0 to 1.0
    detected_features: AudioFeatures
    matched_patterns: List[str]


class TinyMLAcousticEngine:
    """
    Simulated TinyML on-device acoustic model (YAMNet/Edge-CNN architecture).
    Processes 1-second 16kHz PCM audio buffers with negligible CPU & battery overhead.
    """

    def __init__(self, sample_rate: int = 16000, confidence_threshold: float = 0.70):
        self.sample_rate = sample_rate
        self.confidence_threshold = confidence_threshold

    def extract_features(self, audio_buffer: np.ndarray) -> AudioFeatures:
        """Extract lightweight acoustic DSP features from PCM buffer."""
        if len(audio_buffer) == 0:
            return AudioFeatures(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Normalize audio if not float
        if audio_buffer.dtype != np.float32 and audio_buffer.dtype != np.float64:
            audio_buffer = audio_buffer.astype(np.float64) / 32768.0

        # RMS Energy & Peak
        rms = float(np.sqrt(np.mean(audio_buffer ** 2)))
        peak = float(np.max(np.abs(audio_buffer)))
        crest = float(peak / (rms + 1e-6))

        # Zero Crossing Rate (ZCR)
        zero_crossings = np.nonzero(np.diff(audio_buffer > 0))[0]
        zcr = float(len(zero_crossings) / len(audio_buffer))

        # FFT for Spectral Features
        fft_vals = np.abs(np.fft.rfft(audio_buffer))
        freqs = np.fft.rfftfreq(len(audio_buffer), 1.0 / self.sample_rate)

        # Spectral Centroid
        fft_sum = np.sum(fft_vals)
        centroid = float(np.sum(freqs * fft_vals) / fft_sum) if fft_sum > 1e-6 else 0.0

        # Spectral Roll-off (85% energy point)
        cumulative_energy = np.cumsum(fft_vals)
        cutoff_energy = 0.85 * fft_sum
        rolloff_idx = np.searchsorted(cumulative_energy, cutoff_energy)
        rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)]) if len(freqs) > 0 else 0.0

        # Spectral Flatness
        positive_fft = fft_vals[fft_vals > 1e-8]
        if len(positive_fft) > 0:
            geom_mean = np.exp(np.mean(np.log(positive_fft)))
            arith_mean = np.mean(positive_fft)
            flatness = float(geom_mean / arith_mean) if arith_mean > 0 else 0.0
        else:
            flatness = 0.0

        return AudioFeatures(
            rms_energy=rms,
            zero_crossing_rate=zcr,
            spectral_centroid_hz=centroid,
            spectral_rolloff_hz=rolloff,
            spectral_flatness=flatness,
            peak_amplitude=peak,
            crest_factor=crest
        )

    def classify_frame(self, audio_buffer: np.ndarray, explicit_keyword: Optional[str] = None) -> AcousticThreatAssessment:
        """
        Classify an audio frame against trained acoustic anomaly signatures.
        """
        features = self.extract_features(audio_buffer)
        patterns = []
        category = AcousticThreatCategory.AMBIENT_NORMAL
        confidence = 0.0
        threat_score = 0.0

        # Keyword trigger
        if explicit_keyword and explicit_keyword.lower() in ["bachao", "help me", "leave me", "save me", "stop"]:
            patterns.append(f"Panic keyword detected: '{explicit_keyword}'")
            category = AcousticThreatCategory.PANIC_KEYWORD
            confidence = 0.95
            threat_score = 0.95

        # Gunshot / Explosion signature: High peak amplitude (>0.80), impulsive crest factor (>6.0) or high spectral flatness
        elif features.peak_amplitude > 0.80 and (features.crest_factor > 5.5 or features.spectral_flatness > 0.30):
            patterns.append(f"Impulsive blast profile (Peak: {features.peak_amplitude:.2f}, Crest: {features.crest_factor:.1f})")
            category = AcousticThreatCategory.GUNSHOT_EXPLOSION
            confidence = 0.94
            threat_score = 1.0

        # Human Scream / Distress Vocalization: High RMS, high spectral centroid (>2000 Hz), high rolloff (>3200 Hz)
        elif features.rms_energy > 0.12 and features.spectral_centroid_hz > 1800.0 and features.spectral_rolloff_hz > 3000.0:
            patterns.append(f"High-frequency harmonic vocal shrieking (Centroid: {features.spectral_centroid_hz:.1f}Hz)")
            category = AcousticThreatCategory.SCREAM_DISTRESS
            confidence = 0.90
            threat_score = 0.92

        # Glass Shatter / Impact: High ZCR (>0.20), very high spectral centroid (>3800 Hz)
        elif features.zero_crossing_rate > 0.20 and features.spectral_centroid_hz > 3500.0 and features.rms_energy > 0.08:
            patterns.append("High-frequency brittle fracture resonance (Glass break)")
            category = AcousticThreatCategory.GLASS_BREAK
            confidence = 0.86
            threat_score = 0.85

        # Violent Struggle / Scuffle: Moderate erratic energy with irregular mid-band bursts
        elif features.rms_energy > 0.10 and 800.0 < features.spectral_centroid_hz < 2200.0 and features.zero_crossing_rate > 0.15:
            patterns.append("Chaotic broadband friction and physical collision pattern")
            category = AcousticThreatCategory.VIOLENT_STRUGGLE
            confidence = 0.76
            threat_score = 0.78

        # Normal speech
        elif features.rms_energy > 0.04:
            category = AcousticThreatCategory.NORMAL_CONVERSATION
            confidence = 0.82
            threat_score = 0.05
        else:
            category = AcousticThreatCategory.AMBIENT_NORMAL
            confidence = 0.90
            threat_score = 0.0

        is_threat = (threat_score >= self.confidence_threshold) and (
            category not in [AcousticThreatCategory.AMBIENT_NORMAL, AcousticThreatCategory.NORMAL_CONVERSATION]
        )

        return AcousticThreatAssessment(
            is_threat=is_threat,
            category=category,
            confidence=confidence,
            threat_score=threat_score,
            detected_features=features,
            matched_patterns=patterns
        )
