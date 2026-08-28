# Rakshak Protocol - Hardware Integration Guide

## 1. Edge Wearable & Mobile SoC Targets
| Component | Supported Hardware | Framework / SDK |
|---|---|---|
| **PPG / Heart Rate Sensor** | Maxim MAX30102, Analog Devices ADPD188GG, Apple Watch, WearOS (Samsung Galaxy Watch, Pixel Watch) | Embedded C / FreeRTOS / Android Health Services API |
| **Microphone & Audio DSP** | I2S MEMS Mic (Knowles SPH0645LM4H, INMP441) | CMSIS-DSP, TFLite Micro |
| **Edge Neural Processor** | ESP32-S3 (Dual Xtensa LX7 + Vector ext), Nordic nRF5340, Apple Neural Engine, Google Tensor TPU | TensorFlow Lite Micro, Edge Impulse, ONNX Runtime Mobile |
| **Cellular / IoT Radio** | Quectel BG95 (LTE-M/NB-IoT), SIMCom SIM7080G, 5G NR RedCap | AT Commands, MQTT TLS 1.3 |

---

## 2. Autonomous Police Drone Integration (MAVLink v2)
The Drone Router bridges with standard flight controllers (Pixhawk 6X, ArduPilot, PX4 Autopilot):
- **Command Protocol**: MAVLink v2 `MAV_CMD_NAV_WAYPOINT` with automated altitude hold at 65m AGL during transit.
- **Payload GPIO**:
  - `GPIO_22`: High-intensity 15,000-lumen visual strobe flasher.
  - `GPIO_23`: 110dB acoustic siren & voice broadcast amplifier.
  - `UART_2`: 3-axis brushless gimbal locked to victim GPS via Kalman filter tracking.
