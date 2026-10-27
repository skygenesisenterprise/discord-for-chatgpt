from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PlannedChange(BaseModel):
    operation: Literal[
        "create_channel",
        "update_channel",
        "create_role",
        "update_role",
        "send_message",
        "create_webhook",
        "delete_resource",
        "moderation",
    ]
    resource_id: str | None = None
    parameters: dict[str, object] = Field(default_factory=dict)


class OperationPlan(BaseModel):
    plan_id: UUID
    guild_id: str
    changes: list[PlannedChange] = Field(min_length=1)
    risk_level: RiskLevel
    expires_at: datetime


class OperationResult(BaseModel):
    operation_id: UUID
    status: Literal[
        "pending",
        "approved",
        "executing",
        "succeeded",
        "failed",
        "expired",
    ]
    message: str
    affected_resources: list[str] = Field(default_factory=list)
