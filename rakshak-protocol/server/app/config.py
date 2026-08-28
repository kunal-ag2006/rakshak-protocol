"""Configuration settings for Rakshak Protocol Server."""

from pydantic import BaseModel
import os


class Settings(BaseModel):
    PROJECT_NAME: str = "Rakshak Protocol - Emergency Drone Dispatch & Evidence Vault"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = os.getenv("RAKSHAK_SECRET_KEY", "rakshak-shared-secret-key-2026")
    MQTT_BROKER_HOST: str = os.getenv("MQTT_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    DRONE_MAX_CRUISE_SPEED_MPS: float = 22.2  # ~80 km/h
    DRONE_BATTERY_RETURN_THRESHOLD_PCT: float = 20.0
    EVIDENCE_HASH_ALGO: str = "SHA-256"


settings = Settings()
