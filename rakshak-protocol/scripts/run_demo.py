#!/usr/bin/env python3
"""
Interactive / Automated End-to-End Live Demonstration of the Rakshak Protocol.
Simulates edge biometric spike, acoustic classification, stealth SOS streaming,
drone dispatch, and cryptographic evidence verification.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulations.run_scenario import run_full_simulation

if __name__ == "__main__":
    run_full_simulation()
