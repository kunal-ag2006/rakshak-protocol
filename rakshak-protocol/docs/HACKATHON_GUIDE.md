# Rakshak Protocol - Hackathon & Pitch Guide

## 1. Problem Statement
Every year, thousands of violent assaults, kidnappings, and hit-and-run incidents occur where victims are rendered unable to unlock their smartphones or call emergency services. Existing SOS apps fail because they assume:
1. The victim has free hands to unlock a screen.
2. The attacker will not notice the victim dialing emergency numbers.
3. Traditional police patrol cars can navigate traffic jams in time.

## 2. The Rakshak Breakthrough
- **Zero-Click Threat Detection**: The system uses on-device Multi-Factor Authentication (MFA) for danger—correlating autonomic panic biomarkers ($\text{HR} > 150 \text{ BPM} + \text{HRV Collapse}$) with TinyML acoustic shrieking/gunshot classifiers.
- **True Stealth Mode**: The smartphone screen stays 100% black; zero haptic vibrations or visible indicators are emitted, preventing assailant retaliation while silently streaming GPS & mic audio.
- **Autonomous Drone Response (<3 Mins)**: Drones pre-positioned on urban cell towers scramble automatically, arriving before patrol cars to deploy visual strobes, sirens, and 4K optical tracking.
- **Judicial Evidence Vault**: Telemetry and audio hashes are written to an append-only SHA-256 cryptographic chain, making evidence tampering mathematically impossible.

## 3. Live Demo Walkthrough
Run the interactive scenario in one command:
```bash
python simulations/run_scenario.py
```
Or start the web dashboard and REST server:
```bash
uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open `http://localhost:8000` to interact with the Emergency Operations Center dashboard.
