"""
Synthetic Biosignal & Acoustic Data Generator for Rakshak Protocol.
Generates realistic PPG waveforms, RR interval series, and acoustic PCM arrays.
"""

import time
from typing import List, Tuple
import numpy as np
from edge_device.biometric_engine import BiometricVitals


def generate_audio_pcm(
    signal_type: str = "ambient",
    duration_sec: float = 1.0,
    sample_rate: int = 16000
) -> np.ndarray:
    """Generate synthetic 16kHz audio buffer matching threat acoustic profiles."""
    num_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)

    if signal_type == "ambient":
        # Low amplitude ambient background
        noise = np.random.normal(0, 0.015, num_samples)
        return noise.astype(np.float32)

    elif signal_type == "scream":
        # High frequency, modulated harmonic shrieking (2200Hz - 3200Hz) with high energy
        base_freq = 2400.0
        modulation = 400.0 * np.sin(2 * np.pi * 6.0 * t)
        freq = base_freq + modulation
        carrier = 0.55 * np.sin(2 * np.pi * freq * t)
        harmonics = 0.25 * np.sin(2 * np.pi * 2.2 * freq * t)
        noise = np.random.normal(0, 0.03, num_samples)
        signal = carrier + harmonics + noise
        return np.clip(signal, -1.0, 1.0).astype(np.float32)

    elif signal_type == "gunshot":
        # Extremely fast rise time, sharp exponential decay shockwave
        decay = np.exp(-35.0 * t)
        blast = 0.95 * np.sin(2 * np.pi * 320.0 * t) * decay
        noise = np.random.normal(0, 0.4, num_samples) * decay
        signal = blast + noise
        return np.clip(signal, -1.0, 1.0).astype(np.float32)

    elif signal_type == "glass_break":
        # High frequency chaotic spikes (4000Hz - 7000Hz)
        high_freq = 0.4 * np.sin(2 * np.pi * 4800.0 * t) + 0.3 * np.sin(2 * np.pi * 6200.0 * t)
        crack_noise = np.random.uniform(-0.3, 0.3, num_samples) * (t < 0.3)
        signal = high_freq + crack_noise
        return np.clip(signal, -1.0, 1.0).astype(np.float32)

    else:
        return np.zeros(num_samples, dtype=np.float32)


def generate_vitals_scenario(scenario_name: str) -> BiometricVitals:
    """Generate biometric vitals for different physiological test scenarios."""
    now = time.time()

    if scenario_name == "nominal_resting":
        # HR ~ 72 BPM, high HRV (healthy parasympathetic tone)
        hr = 72.0
        rr_base = 60000.0 / hr
        rr_series = [rr_base + float(np.random.normal(0, 35.0)) for _ in range(15)]
        return BiometricVitals(
            timestamp=now,
            heart_rate_bpm=hr,
            rr_intervals_ms=rr_series,
            spo2_percentage=99.0,
            skin_conductance_us=1.8,
            accelerometer_magnitude=1.02
        )

    elif scenario_name == "exercise_jogging":
        # High HR (142 BPM), moderate HRV (RMSSD > 25ms) with high accelerometer motion (False positive filter test)
        hr = 142.0
        rr_base = 60000.0 / hr
        rr_series = [rr_base + float(np.random.normal(0, 28.0)) for _ in range(15)]
        return BiometricVitals(
            timestamp=now,
            heart_rate_bpm=hr,
            rr_intervals_ms=rr_series,
            spo2_percentage=97.0,
            skin_conductance_us=6.5,
            accelerometer_magnitude=4.8  # Jogging motion
        )

    elif scenario_name == "acute_panic_attack_assault":
        # Extreme Tachycardia (165 BPM) + Severe HRV collapse (RMSSD ~ 3ms) + Galvanic Surge
        hr = 166.0
        rr_base = 60000.0 / hr
        # Very rigid RR interval (almost 0 variance - autonomic freeze)
        rr_series = [rr_base + float(np.random.normal(0, 2.0)) for _ in range(15)]
        return BiometricVitals(
            timestamp=now,
            heart_rate_bpm=hr,
            rr_intervals_ms=rr_series,
            spo2_percentage=94.0,
            skin_conductance_us=18.2,
            accelerometer_magnitude=1.4
        )

    else:
        return BiometricVitals(timestamp=now, heart_rate_bpm=75.0, rr_intervals_ms=[800.0]*10)
