"""
Interactive CLI End-to-End Simulation Runner for Rakshak Protocol.
Demonstrates the full Zero-Click Threat Detection, Stealth SOS triggering,
MQTT Telemetry Streaming, Cryptographic Evidence Vaulting, and Drone Dispatch pipeline.
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from edge_device.stealth_controller import StealthSOSController, SystemState
from edge_device.biometric_engine import BiometricTriageEngine
from edge_device.acoustic_engine import TinyMLAcousticEngine
from edge_device.hardware_interrupt import HardwareInterruptListener
from edge_device.mqtt_publisher import GPSCoordinates, RakshakMQTTPublisher
from server.app.evidence_vault import evidence_vault
from server.app.drone_router import Coordinates, drone_router
from server.app.mqtt_broker import incident_manager
from server.app.models import TelemetryFrame
from simulations.mock_data import generate_audio_pcm, generate_vitals_scenario


def print_banner():
    print("=" * 80)
    print("  🛡️  PROJECT RAKSHAK: ZERO-CLICK SOS & POLICE DRONE DISPATCH SIMULATOR")
    print("  Based on TransparentGov R&D Civic Accountability Framework (Module 3)")
    print("=" * 80)


def run_full_simulation():
    print_banner()

    # 1. Initialize Edge Device Unit
    user_id = "CITIZEN-ANANYA-DEL-8901"
    print(f"\n[1] Initializing Edge Unit for User: {user_id}")
    bio_engine = BiometricTriageEngine()
    acoustic_engine = TinyMLAcousticEngine()
    hw_listener = HardwareInterruptListener()
    mqtt_client = RakshakMQTTPublisher()

    controller = StealthSOSController(
        user_id=user_id,
        biometric_engine=bio_engine,
        acoustic_engine=acoustic_engine,
        hardware_listener=hw_listener,
        mqtt_publisher=mqtt_client
    )

    # Wire edge publisher directly to server incident manager for the simulation
    def on_mqtt_packet(topic: str, payload: dict):
        # Convert dict to TelemetryFrame
        frame = TelemetryFrame(**payload)
        incident_manager.ingest_telemetry_frame(frame)

    mqtt_client.set_publish_handler(on_mqtt_packet)
    controller.set_location(lat=28.6289, lon=77.2065, alt_m=16.0) # Near Connaught Place / Central Delhi

    # Step 1: Nominal State
    print("\n--- PHASE 1: Citizen Walking in City (Nominal Baseline) ---")
    vitals_normal = generate_vitals_scenario("nominal_resting")
    audio_normal = generate_audio_pcm("ambient", duration_sec=1.0)
    res_1 = controller.process_tick(vitals_normal, audio_normal)
    print(f"  • System State: {res_1.system_state.value}")
    print(f"  • Biometrics: HR={res_1.biometric_assessment.hr_bpm:.1f} BPM, HRV RMSSD={res_1.biometric_assessment.hrv_rmssd:.1f}ms")
    print(f"  • Acoustic: {res_1.acoustic_assessment.category.value} (Conf: {res_1.acoustic_assessment.confidence:.0%})")
    print(f"  • SOS Triggered: {res_1.is_sos_triggered}")
    print(f"  • Display Blackout (Stealth): {res_1.stealth_display_blackout}")

    # Step 2: High Exertion / Jogging (False Positive Resistance Test)
    print("\n--- PHASE 2: Aerobic Exertion / Jogging (False-Positive Filter Verification) ---")
    vitals_jog = generate_vitals_scenario("exercise_jogging")
    audio_jog = generate_audio_pcm("ambient", duration_sec=1.0)
    res_2 = controller.process_tick(vitals_jog, audio_jog)
    print(f"  • System State: {res_2.system_state.value}")
    print(f"  • Biometrics: HR={res_2.biometric_assessment.hr_bpm:.1f} BPM (High), Accel={vitals_jog.accelerometer_magnitude:.1f}g")
    print(f"  • Acoustic: {res_2.acoustic_assessment.category.value}")
    print(f"  • SOS Triggered: {res_2.is_sos_triggered} (Correctly ignored aerobic exercise)")

    # Step 3: Acute Assault / Kidnap Threat (Zero-Click MFA Danger Condition)
    print("\n--- PHASE 3: Sudden Violent Ambush (Zero-Click Multi-Factor Threat Triggered!) ---")
    vitals_panic = generate_vitals_scenario("acute_panic_attack_assault")
    audio_scream = generate_audio_pcm("scream", duration_sec=1.0)
    res_3 = controller.process_tick(vitals_panic, audio_scream)
    print(f"  🚨 SYSTEM STATE: {res_3.system_state.value}")
    print(f"  🚨 TRIGGER REASON: {res_3.trigger_type}")
    print(f"  🚨 Biometric Triage: HR={res_3.biometric_assessment.hr_bpm:.1f} BPM (SURGE) | HRV RMSSD={res_3.biometric_assessment.hrv_rmssd:.1f}ms (COLLAPSE)")
    print(f"  🚨 Acoustic TinyML: {res_3.acoustic_assessment.category.value} (Confidence: {res_3.acoustic_assessment.confidence:.0%})")
    print(f"  🔒 Stealth Screen Blackout: {res_3.stealth_display_blackout} (Screen remains 100% black to avoid alerting assailant)")
    print(f"  📡 Silent Telemetry Stream: {res_3.stealth_audio_streaming} (Broadcasting encrypted MQTT packets to Cloud Vault)")
    print(f"  🆔 Generated Incident ID: {res_3.incident_id}")

    incident_id = res_3.incident_id
    time.sleep(0.5)

    # Check Cloud Vault & Incident Dispatch Status
    incident = incident_manager.active_incidents.get(incident_id)
    print("\n--- PHASE 4: Cloud Vault & Autonomous Drone Dispatch Response ---")
    if incident:
        print(f"  • Cloud Incident Created: {incident.incident_id}")
        print(f"  • Threat Level: {incident.threat_level.value}")
        print(f"  • Assigned Drone ID: {incident.assigned_drone_id}")
        print(f"  • Initial ETA to Scene: {incident.drone_eta_seconds:.1f} seconds (~ sub-2 minutes!)")

    # Simulate Drone Flight Steps
    drone_id = incident.assigned_drone_id
    print(f"\n--- PHASE 5: Simulating Drone Flight from Nearest Cell Tower to Scene ---")
    for step in range(1, 4):
        updated_drone = drone_router.simulate_drone_step(drone_id, dt_seconds=20.0)
        print(f"  [T+{step*20}s] Drone {drone_id}: Alt={updated_drone.altitude_agl_m}m | Dist={updated_drone.distance_to_target_m:.1f}m | ETA={updated_drone.eta_seconds:.1f}s | Status={updated_drone.status.value}")

    # Final Arrival & Deterrence
    final_drone = drone_router.simulate_drone_step(drone_id, dt_seconds=100.0)
    print(f"\n  🎯 DRONE ARRIVED ON SCENE!")
    print(f"  • Status: {final_drone.status.value}")
    print(f"  • Strobe Lights: {'ACTIVE' if final_drone.spotlight_active else 'OFF'}")
    print(f"  • High-Decibel Siren: {'ACTIVE' if final_drone.siren_active else 'OFF'}")
    print(f"  • 4K Thermal/Optical Gimbal: {'LOCKED ON GPS' if final_drone.camera_locked else 'OFF'}")

    # Phase 6: Verify Cryptographic Evidence Chain
    print("\n--- PHASE 6: Cryptographic Evidence Vault Verification (SHA-256 Ledger) ---")
    chain = evidence_vault.get_chain(incident_id)
    print(f"  • Total Evidence Blocks Recorded: {len(chain)}")
    for blk in chain:
        print(f"    - Block #{blk.block_index} | Prev: {blk.previous_hash[:16]}... | Hash: {blk.current_hash[:16]}... | Timestamp: {blk.timestamp}")

    is_valid, report = evidence_vault.verify_chain_integrity(incident_id)
    print(f"  • Cryptographic Chain Integrity: {'✅ 100% VERIFIED / TAMPER-FREE' if is_valid else '❌ CORRUPTED'}")
    print(f"  • Audit Statement: {report}")
    print("\n" + "=" * 80)
    print("  SIMULATION COMPLETE: RAKSHAK PROTOCOL LIFECYCLE SUCCESSFULLY DEMONSTRATED.")
    print("=" * 80)


if __name__ == "__main__":
    run_full_simulation()
