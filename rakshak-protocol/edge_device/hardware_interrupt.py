"""
Hardware Interrupt Engine for Rakshak Protocol.
Maps OS-level physical button events (e.g. 3-second long press on Power/Side key)
to trigger immediate hardware override of the Zero-Click SOS logic.
"""

from dataclasses import dataclass
from enum import Enum
import time
from typing import Callable, List, Optional


class ButtonEventType(str, Enum):
    PRESS_DOWN = "PRESS_DOWN"
    RELEASE = "RELEASE"
    LONG_PRESS_HOLD = "LONG_PRESS_HOLD"
    MULTI_TAP_PANIC = "MULTI_TAP_PANIC"


@dataclass
class HardwareInterruptEvent:
    event_type: ButtonEventType
    button_name: str
    duration_seconds: float
    timestamp: float
    is_emergency_trigger: bool
    override_reason: str


class HardwareInterruptListener:
    """
    Simulated OS-level hardware key listener.
    Monitors kernel GPIO / Android Accessibility / iOS Lock Screen physical interrupts.
    """

    def __init__(self, long_press_threshold_sec: float = 3.0, tap_window_sec: float = 1.5):
        self.long_press_threshold_sec = long_press_threshold_sec
        self.tap_window_sec = tap_window_sec

        self._button_down_time: Optional[float] = None
        self._recent_taps: List[float] = []
        self._listeners: List[Callable[[HardwareInterruptEvent], None]] = []

    def register_callback(self, callback: Callable[[HardwareInterruptEvent], None]):
        """Register listener for emergency hardware triggers."""
        self._listeners.append(callback)

    def trigger_button_down(self, button_name: str = "POWER_KEY", timestamp: Optional[float] = None) -> Optional[HardwareInterruptEvent]:
        """Simulate user holding down physical hardware key."""
        now = timestamp or time.time()
        self._button_down_time = now
        return None

    def trigger_button_up(self, button_name: str = "POWER_KEY", timestamp: Optional[float] = None) -> HardwareInterruptEvent:
        """Simulate user releasing physical hardware key."""
        now = timestamp or time.time()
        start = self._button_down_time or now
        duration = max(0.0, now - start)
        self._button_down_time = None

        # Check 3-second long press hold
        if duration >= self.long_press_threshold_sec:
            event = HardwareInterruptEvent(
                event_type=ButtonEventType.LONG_PRESS_HOLD,
                button_name=button_name,
                duration_seconds=duration,
                timestamp=now,
                is_emergency_trigger=True,
                override_reason=f"Physical {button_name} held for {duration:.2f}s (>= {self.long_press_threshold_sec}s threshold)"
            )
            self._notify(event)
            return event

        # Check rapid multi-tap panic pattern (e.g. 4 rapid clicks in 1.5s)
        self._recent_taps.append(now)
        self._recent_taps = [t for t in self._recent_taps if now - t <= self.tap_window_sec]

        if len(self._recent_taps) >= 4:
            event = HardwareInterruptEvent(
                event_type=ButtonEventType.MULTI_TAP_PANIC,
                button_name=button_name,
                duration_seconds=duration,
                timestamp=now,
                is_emergency_trigger=True,
                override_reason=f"Panic multi-tap detected ({len(self._recent_taps)} taps in {self.tap_window_sec}s)"
            )
            self._recent_taps.clear()
            self._notify(event)
            return event

        event = HardwareInterruptEvent(
            event_type=ButtonEventType.RELEASE,
            button_name=button_name,
            duration_seconds=duration,
            timestamp=now,
            is_emergency_trigger=False,
            override_reason="Normal short press"
        )
        return event

    def _notify(self, event: HardwareInterruptEvent):
        for cb in self._listeners:
            try:
                cb(event)
            except Exception as e:
                print(f"[HardwareInterrupt] Error in listener callback: {e}")
