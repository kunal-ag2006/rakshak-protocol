"""
Biometric Triage Engine for Rakshak Protocol.
Analyzes Photoplethysmography (PPG) and Heart Rate Variability (HRV) metrics in real-time
to detect physiological markers of acute terror, panic, and physical struggle.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np
import time


@dataclass
class BiometricVitals:
    timestamp: float
    heart_rate_bpm: float
    rr_intervals_ms: List[float]
    spo2_percentage: float = 98.0
    skin_conductance_us: float = 2.5
    accelerometer_magnitude: float = 1.0


@dataclass
class HRVMetrics:
    mean_rr_ms: float
    sdnn_ms: float       # Standard deviation of NN intervals
    rmssd_ms: float      # Root mean square of successive differences
    pnn50_pct: float     # Percentage of successive RR intervals differing > 50ms
    stress_index: float  # Baevsky stress index metric


@dataclass
class BiometricThreatAssessment:
    is_threat: bool
    threat_score: float  # 0.0 to 1.0
    hr_bpm: float
    hrv_rmssd: float
    hrv_sdnn: float
    stress_index: float
    reason: str
    confidence: float


class BiometricTriageEngine:
    """
    On-device lightweight biometric processor.
    Detects sudden sympathetic nervous system surge (acute tachycardia + HRV collapse)
    characteristic of violent assault or acute terror.
    """

    def __init__(
        self,
        hr_panic_threshold: float = 150.0,
        hr_spike_delta_threshold: float = 40.0,
        hrv_rmssd_critical_low: float = 18.0,
        hrv_sdnn_critical_low: float = 20.0,
        sliding_window_size: int = 30
    ):
        self.hr_panic_threshold = hr_panic_threshold
        self.hr_spike_delta_threshold = hr_spike_delta_threshold
        self.hrv_rmssd_critical_low = hrv_rmssd_critical_low
        self.hrv_sdnn_critical_low = hrv_sdnn_critical_low
        self.sliding_window_size = sliding_window_size

        self._baseline_hr: float = 72.0
        self._history_rr: List[float] = []
        self._history_hr: List[float] = []

    def set_baseline(self, baseline_hr: float):
        """Calibrate user baseline resting heart rate."""
        self._baseline_hr = max(40.0, min(100.0, baseline_hr))

    def compute_hrv(self, rr_intervals: List[float]) -> HRVMetrics:
        """Compute standard HRV time-domain metrics from R-R interval sequence (in ms)."""
        if len(rr_intervals) < 2:
            return HRVMetrics(
                mean_rr_ms=800.0,
                sdnn_ms=50.0,
                rmssd_ms=40.0,
                pnn50_pct=20.0,
                stress_index=50.0
            )

        rr = np.array(rr_intervals, dtype=np.float64)
        mean_rr = float(np.mean(rr))
        sdnn = float(np.std(rr, ddof=1)) if len(rr) > 1 else 0.0

        successive_diffs = np.diff(rr)
        rmssd = float(np.sqrt(np.mean(successive_diffs ** 2))) if len(successive_diffs) > 0 else 0.0

        nn50_count = np.sum(np.abs(successive_diffs) > 50.0)
        pnn50 = float((nn50_count / len(successive_diffs)) * 100.0) if len(successive_diffs) > 0 else 0.0

        # Simplified Baevsky Stress Index
        var_range = max(1.0, float(np.ptp(rr)))
        stress_index = float((1000.0 / (2.0 * max(100.0, mean_rr) * (var_range / 1000.0))))

        return HRVMetrics(
            mean_rr_ms=mean_rr,
            sdnn_ms=sdnn,
            rmssd_ms=rmssd,
            pnn50_pct=pnn50,
            stress_index=stress_index
        )

    def evaluate_vitals(self, vitals: BiometricVitals) -> BiometricThreatAssessment:
        """
        Evaluate real-time vitals against threat thresholds.
        Condition A: (HR > 150 BPM OR Sudden Surge > baseline + 40 BPM) AND (HRV RMSSD < 18ms)
        """
        self._history_hr.append(vitals.heart_rate_bpm)
        if len(self._history_hr) > self.sliding_window_size:
            self._history_hr.pop(0)

        recent_rr = vitals.rr_intervals_ms if vitals.rr_intervals_ms and len(vitals.rr_intervals_ms) >= 3 else [60000.0 / max(30.0, vitals.heart_rate_bpm)] * 10
        hrv = self.compute_hrv(recent_rr)

        current_hr = vitals.heart_rate_bpm
        hr_delta_from_baseline = current_hr - self._baseline_hr

        # Threat condition calculations
        hr_extreme = current_hr >= self.hr_panic_threshold
        hr_surge = hr_delta_from_baseline >= self.hr_spike_delta_threshold
        hrv_collapsed = hrv.rmssd_ms <= self.hrv_rmssd_critical_low

        score = 0.0
        reasons = []

        if hr_extreme:
            score += 0.55
            reasons.append(f"Extreme Tachycardia ({current_hr:.1f} BPM >= {self.hr_panic_threshold} BPM)")
        elif hr_surge:
            score += 0.40
            reasons.append(f"Acute HR Surge (+{hr_delta_from_baseline:.1f} BPM over baseline)")

        if hrv_collapsed:
            score += 0.45
            reasons.append(f"Critical Autonomic HRV Collapse (RMSSD={hrv.rmssd_ms:.1f}ms <= {self.hrv_rmssd_critical_low}ms)")

        # Exercise discrimination: if high physical movement accompanies HR increase without acute HRV collapse
        is_exercise = (vitals.accelerometer_magnitude > 3.0) and not hrv_collapsed
        if is_exercise:
            score = max(0.0, score - 0.50)
            reasons.append("Movement artifact / High physical cadence detected (Aerobic exertion damping)")

        threat_score = min(1.0, max(0.0, score))
        is_threat = (hr_extreme or hr_surge) and hrv_collapsed and not is_exercise

        return BiometricThreatAssessment(
            is_threat=is_threat,
            threat_score=threat_score,
            hr_bpm=current_hr,
            hrv_rmssd=hrv.rmssd_ms,
            hrv_sdnn=hrv.sdnn_ms,
            stress_index=hrv.stress_index,
            reason="; ".join(reasons) if reasons else "Normal physiological state",
            confidence=0.92 if is_threat else 0.85
        )
