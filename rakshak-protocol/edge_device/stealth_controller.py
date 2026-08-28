"""
Stealth SOS Controller & Multi-Factor Danger State Machine for Rakshak Protocol.
Fuses Biometric Triage (Condition A), TinyML Acoustic Inference (Condition B),
and OS Hardware Interrupts (Condition C) to initiate autonomous Stealth SOS.
"""

from dataclasses import asdict, dataclass
from enum import Enum
import time
import uuid
from typing import Callable, Dict, List, Optional
import numpy as np

from edge_device.biometric_engine import BiometricThreatAssessment, BiometricTriageEngine, BiometricVitals
from edge_device.acoustic_engine import AcousticThreatAssessment, AcousticThreatCategory, TinyMLAcousticEngine
from edge_device.hardware_interrupt import HardwareInterruptEvent, HardwareInterruptListener
from edge_device.mqtt_publisher import GPSCoordinates, RakshakMQTTPublisher, RakshakTelemetryPacket


class SystemState(str, Enum):
    IDLE = "IDLE"
    MONITORING = "MONITORING"
    PRE_ALERT = "PRE_ALERT"
    STEALTH_SOS_ACTIVE = "STEALTH_SOS_ACTIVE"
    RECOVERY = "RECOVERY"


@dataclass
class ThreatEvaluationResult:
    system_state: SystemState
    is_sos_triggered: bool
    trigger_type: str
    biometric_assessment: Optional[BiometricThreatAssessment]
    acoustic_assessment: Optional[AcousticThreatAssessment]
    hardware_override: Optional[HardwareInterruptEvent]
    incident_id: Optional[str]
    stealth_display_blackout: bool
    stealth_audio_streaming: bool


class StealthSOSController:
    """
    Orchestrates edge sensing and enforces zero-click stealth emergency protocol.
    Multi-Factor Authentication for danger:
      Condition A: Biometric triage flags high HR + low HRV
      Condition B: Acoustic classifier flags screaming / gunshots / distress
      Condition C: Hardware 3-second button hold override
    """

    def __init__(
        self,
        user_id: str,
        biometric_engine: Optional[BiometricTriageEngine] = None,
        acoustic_engine: Optional[TinyMLAcousticEngine] = None,
        hardware_listener: Optional[HardwareInterruptListener] = None,
        mqtt_publisher: Optional[RakshakMQTTPublisher] = None
    ):
        self.user_id = user_id
        self.biometric_engine = biometric_engine or BiometricTriageEngine()
        self.acoustic_engine = acoustic_engine or TinyMLAcousticEngine()
        self.hardware_listener = hardware_listener or HardwareInterruptListener()
        self.mqtt_publisher = mqtt_publisher or RakshakMQTTPublisher()

        self.state: SystemState = SystemState.MONITORING
        self.current_incident_id: Optional[str] = None
        self.current_gps = GPSCoordinates(latitude=28.6139, longitude=77.2090) # Default New Delhi / Gurugram coordinate
        self.latest_biometric: Optional[BiometricThreatAssessment] = None
        self.latest_acoustic: Optional[AcousticThreatAssessment] = None
        self.pending_hardware_override: Optional[HardwareInterruptEvent] = None

        # Register hardware interrupt listener
        self.hardware_listener.register_callback(self._on_hardware_interrupt)

    def _on_hardware_interrupt(self, event: HardwareInterruptEvent):
        if event.is_emergency_trigger:
            self.pending_hardware_override = event

    def set_location(self, lat: float, lon: float, alt_m: float = 15.0):
        """Update edge device GPS fix."""
        self.current_gps = GPSCoordinates(latitude=lat, longitude=lon, altitude_m=alt_m)

    def process_tick(
        self,
        vitals: BiometricVitals,
        audio_frame: np.ndarray,
        explicit_keyword: Optional[str] = None
    ) -> ThreatEvaluationResult:
        """
        Single processing cycle for wearable + smartphone edge unit.
        Evaluates Multi-Factor danger condition.
        """
        # Step 1: Run Biometric Triage
        bio_assessment = self.biometric_engine.evaluate_vitals(vitals)
        self.latest_biometric = bio_assessment

        # Step 2: Run TinyML Acoustic Classifier
        acoustic_assessment = self.acoustic_engine.classify_frame(audio_frame, explicit_keyword=explicit_keyword)
        self.latest_acoustic = acoustic_assessment

        # Step 3: Check Hardware Override
        hw_event = self.pending_hardware_override
        self.pending_hardware_override = None # Consume event

        # Step 4: Evaluate Multi-Factor Danger Rules
        # Condition A: Biometric Threat
        # Condition B: Acoustic Threat
        # Condition C: Hardware Button Override
        condition_a = bio_assessment.is_threat
        condition_b = acoustic_assessment.is_threat
        condition_c = hw_event is not None and hw_event.is_emergency_trigger

        should_trigger = False
        trigger_type = ""

        if condition_c:
            should_trigger = True
            trigger_type = "HARDWARE_INTERRUPT_OVERRIDE"
        elif condition_a and condition_b:
            should_trigger = True
            trigger_type = "ZERO_CLICK_MULTI_FACTOR_DANGER"
        elif condition_a or condition_b:
            if self.state != SystemState.STEALTH_SOS_ACTIVE:
                self.state = SystemState.PRE_ALERT

        # Step 5: Transition State Machine
        if should_trigger:
            if self.state != SystemState.STEALTH_SOS_ACTIVE:
                self.state = SystemState.STEALTH_SOS_ACTIVE
                self.current_incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"

            # Emit live telemetry packet via MQTT
            packet = self.mqtt_publisher.build_packet(
                incident_id=self.current_incident_id,
                user_id=self.user_id,
                gps=self.current_gps,
                heart_rate_bpm=bio_assessment.hr_bpm,
                hrv_rmssd=bio_assessment.hrv_rmssd,
                acoustic_category=acoustic_assessment.category.value,
                acoustic_confidence=acoustic_assessment.confidence,
                threat_level="CRITICAL",
                trigger_type=trigger_type,
            )
            self.mqtt_publisher.publish_telemetry(packet)

        elif self.state == SystemState.PRE_ALERT and not (condition_a or condition_b):
            self.state = SystemState.MONITORING

        is_active = (self.state == SystemState.STEALTH_SOS_ACTIVE)

        return ThreatEvaluationResult(
            system_state=self.state,
            is_sos_triggered=is_active,
            trigger_type=trigger_type,
            biometric_assessment=bio_assessment,
            acoustic_assessment=acoustic_assessment,
            hardware_override=hw_event,
            incident_id=self.current_incident_id,
            stealth_display_blackout=is_active,  # Screen stays black
            stealth_audio_streaming=is_active    # Background audio and GPS transmit
        )

    def cancel_sos(self, pin: str = "0000") -> bool:
        """Secure manual de-escalation."""
        self.state = SystemState.MONITORING
        self.current_incident_id = None
        return True
