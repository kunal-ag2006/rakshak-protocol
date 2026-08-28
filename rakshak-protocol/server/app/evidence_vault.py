"""
Cryptographic Evidence Vault for Rakshak Protocol.
Creates an append-only, tamper-evident hash-chained ledger of all incoming
biometric, acoustic, GPS, and drone video metadata to ensure judicial admissibility.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple
from server.app.models import EvidenceBlock, TelemetryFrame, dump_model


class CryptographicEvidenceVault:
    """
    Append-only evidence chain ensuring mathematical immutability (Module 1/3 compliance).
    Every incoming packet is hashed, chained to previous block hash, and permanently sealed.
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self):
        # Maps incident_id -> List of EvidenceBlocks
        self._chains: Dict[str, List[EvidenceBlock]] = {}

    def _compute_sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def seal_frame(self, telemetry: TelemetryFrame, raw_audio_digest: Optional[str] = None) -> EvidenceBlock:
        """Append incoming telemetry frame to incident evidence chain."""
        incident_id = telemetry.incident_id
        if incident_id not in self._chains:
            self._chains[incident_id] = []

        chain = self._chains[incident_id]
        block_index = len(chain)
        previous_hash = chain[-1].current_hash if chain else self.GENESIS_HASH

        telemetry_dict = dump_model(telemetry)
        telemetry_canonical = json.dumps(telemetry_dict, sort_keys=True)
        telemetry_hash = self._compute_sha256(telemetry_canonical)

        payload_data = {
            "telemetry": telemetry_dict,
            "raw_audio_digest": raw_audio_digest or self._compute_sha256(f"audio-{incident_id}-{block_index}"),
            "recorded_at_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(telemetry.timestamp)),
        }

        block_header = f"{block_index}|{incident_id}|{telemetry.timestamp}|{previous_hash}|{telemetry_hash}"
        current_hash = self._compute_sha256(block_header + "|" + json.dumps(payload_data, sort_keys=True))

        block = EvidenceBlock(
            block_index=block_index,
            incident_id=incident_id,
            timestamp=telemetry.timestamp,
            previous_hash=previous_hash,
            telemetry_hash=telemetry_hash,
            data=payload_data,
            current_hash=current_hash,
        )

        chain.append(block)
        return block

    def get_chain(self, incident_id: str) -> List[EvidenceBlock]:
        """Return full ledger chain for an incident."""
        return self._chains.get(incident_id, [])

    def verify_chain_integrity(self, incident_id: str) -> Tuple[bool, str]:
        """
        Verify all cryptographic links in the chain from genesis to tip.
        Returns (is_valid, report_message).
        """
        chain = self._chains.get(incident_id, [])
        if not chain:
            return True, "Chain is empty (no blocks recorded yet)."

        for i, block in enumerate(chain):
            # Check index sequence
            if block.block_index != i:
                return False, f"Integrity Failure: Block index mismatch at step {i} (found {block.block_index})."

            # Check previous hash link
            expected_prev = chain[i - 1].current_hash if i > 0 else self.GENESIS_HASH
            if block.previous_hash != expected_prev:
                return False, f"Integrity Failure: Hash chain broken at block {i}. Prev hash does not match previous block."

            # Verify telemetry hash
            telemetry_dict = block.data.get("telemetry", {})
            recomputed_tel_hash = self._compute_sha256(json.dumps(telemetry_dict, sort_keys=True))
            if recomputed_tel_hash != block.telemetry_hash:
                return False, f"Integrity Failure: Telemetry content tampering detected in block {i}."

            # Verify current block hash
            block_header = f"{block.block_index}|{block.incident_id}|{block.timestamp}|{block.previous_hash}|{block.telemetry_hash}"
            recomputed_curr_hash = self._compute_sha256(block_header + "|" + json.dumps(block.data, sort_keys=True))
            if recomputed_curr_hash != block.current_hash:
                return False, f"Integrity Failure: Block hash corrupted at block {i}."

        return True, f"Cryptographic integrity verified: {len(chain)} blocks intact with valid SHA-256 chain."


# Singleton instance
evidence_vault = CryptographicEvidenceVault()
