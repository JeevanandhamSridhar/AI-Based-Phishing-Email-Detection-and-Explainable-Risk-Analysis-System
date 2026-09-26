"""Health Check Schemas

Defines response structures for system readiness and module telemetry.
"""

from typing import Dict
from pydantic import BaseModel, Field


class SafetyStatus(BaseModel):
    offline_only: bool = Field(..., description="Local-first offline mode enforced")
    network_fetch_blocked: bool = Field(..., description="Active outbound URL fetching is disabled")
    attachment_execution_blocked: bool = Field(..., description="Active attachment execution is disabled")


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    version: str = Field(..., examples=["1.0.0"])
    timestamp: str = Field(..., examples=["2026-09-26T22:30:00Z"])
    environment: str = Field(..., examples=["development"])
    modules: Dict[str, str] = Field(
        ...,
        description="Individual status of analytical and ML modules",
    )
    database: str = Field(..., examples=["connected"])
    safety: SafetyStatus
    weights_valid: bool = Field(..., description="Whether risk scoring weights sum to 100.0")
