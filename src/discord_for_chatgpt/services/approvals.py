import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models import Approval, ApprovalPlan, AuditLog


class ApprovalService:
    @staticmethod
    def compute_plan_hash(plan_data: dict[str, Any]) -> str:
        payload = json.dumps(plan_data, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    @staticmethod
    async def create_plan(
        session: AsyncSession,
        user_id: Optional[str],
        action: str,
        parameters: dict[str, Any],
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        guild_id: Optional[str] = None,
        channel_id: Optional[str] = None,
        risk_level: str = "medium",
        expires_minutes: int = 10,
    ) -> ApprovalPlan:
        plan_data = {
            "action": action,
            "parameters": parameters,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
        }
        plan_hash = ApprovalService.compute_plan_hash(plan_data)
        plan = ApprovalPlan(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            guild_id=guild_id,
            channel_id=channel_id,
            parameters=parameters,
            risk_level=risk_level,
            status="pending",
            plan_hash=plan_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=expires_minutes),
        )
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan

    @staticmethod
    async def approve_plan(
        session: AsyncSession,
        plan_id: str,
        approver_id: str,
    ) -> ApprovalPlan:
        # Lock semantics with select
        result = await session.execute(select(ApprovalPlan).where(ApprovalPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise ValueError("Plan not found")
        if plan.status != "pending":
            raise ValueError("Plan not in pending state")
        if plan.expires_at < datetime.utcnow():
            plan.status = "expired"
            await session.commit()
            raise ValueError("Plan expired")
        # Check if already consumed/approved
        if plan.consumed_at is not None:
            raise ValueError("Plan already consumed")
        # Create approval
        approval = Approval(plan_id=plan.id, approver_id=approver_id)
        session.add(approval)
        plan.status = "approved"
        plan.approved_by = approver_id
        plan.approved_at = datetime.utcnow()
        await session.commit()
        await session.refresh(plan)
        await ApprovalService.audit(session, approver_id, "plan_approved", plan)
        return plan

    @staticmethod
    async def validate_and_consume(
        session: AsyncSession,
        plan_id: str,
        approver_id: Optional[str] = None,
    ) -> ApprovalPlan:
        result = await session.execute(select(ApprovalPlan).where(ApprovalPlan.id == plan_id))
        plan = result.scalar_one_or_none()
        if not plan:
            raise ValueError("Plan not found")
        if plan.status != "approved":
            raise ValueError("Plan not approved")
        if plan.expires_at < datetime.utcnow():
            plan.status = "expired"
            await session.commit()
            raise ValueError("Plan expired")
        if plan.consumed_at is not None:
            raise ValueError("Plan already consumed")
        # Mark as consumed (single use)
        plan.consumed_at = datetime.utcnow()
        plan.status = "consumed"
        await session.commit()
        await session.refresh(plan)
        await ApprovalService.audit(session, approver_id, "plan_consumed", plan)
        return plan

    @staticmethod
    async def audit(session: AsyncSession, user_id: Optional[str], action: str, plan: ApprovalPlan, details: Optional[dict] = None):
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=plan.resource_type,
            resource_id=plan.resource_id,
            guild_id=plan.guild_id,
            plan_id=plan.id,
            status="ok",
            details=details,
        )
        session.add(log)
        await session.commit()
