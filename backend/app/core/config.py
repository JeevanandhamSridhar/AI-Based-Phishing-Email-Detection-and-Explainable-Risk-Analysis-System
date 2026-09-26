"""Application Configuration Module

Loads environment variables, defines safety invariants, risk weighting parameters,
and filesystem directories using Pydantic Settings.
"""

from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", ".env.example", "../.env.example"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core Application Metadata
    PROJECT_NAME: str = "AI-Based Phishing Email Detection and Explainable Risk Analysis System"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Local Persistence
    DATABASE_URL: str = "sqlite:///./phishing_risk_analyzer.db"

    # Strict Defensive Safety Invariants
    OFFLINE_ONLY: bool = True
    ALLOW_NETWORK_FETCH: bool = False
    ALLOW_ATTACHMENT_EXECUTION: bool = False

    # Configurable Risk Engine Weights (Must sum to 100.0)
    WEIGHT_ML_PHISHING: float = Field(default=30.0, description="Weight for ML probability score")
    WEIGHT_URL_RISK: float = Field(default=20.0, description="Weight for static URL risk score")
    WEIGHT_HEADER_AUTH: float = Field(default=15.0, description="Weight for header/auth failure score")
    WEIGHT_SENDER_DOMAIN: float = Field(default=10.0, description="Weight for sender typosquatting/lookalike score")
    WEIGHT_SOCIAL_ENG: float = Field(default=10.0, description="Weight for social engineering heuristic triggers")
    WEIGHT_ATTACHMENT: float = Field(default=10.0, description="Weight for static attachment risk score")
    WEIGHT_CONTENT: float = Field(default=5.0, description="Weight for content obfuscation/anomaly score")

    # Categorical Risk Thresholds (Project-defined defaults, not universal standards)
    THRESHOLD_LOW: float = 25.0
    THRESHOLD_MODERATE: float = 50.0
    THRESHOLD_HIGH: float = 75.0

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    REPORTS_DIR: str = "./reports/generated"
    MODELS_DIR: str = "./models"
    DATA_DIR: str = "./data"

    # CORS Allow List for Local React Dashboard
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    def validate_weights(self) -> bool:
        """Validates that all component weights sum to exactly 100.0."""
        total = (
            self.WEIGHT_ML_PHISHING
            + self.WEIGHT_URL_RISK
            + self.WEIGHT_HEADER_AUTH
            + self.WEIGHT_SENDER_DOMAIN
            + self.WEIGHT_SOCIAL_ENG
            + self.WEIGHT_ATTACHMENT
            + self.WEIGHT_CONTENT
        )
        return abs(total - 100.0) < 0.001


settings = Settings()
