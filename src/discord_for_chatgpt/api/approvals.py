from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.session import get_session
from ..services.approvals import ApprovalService

router = APIRouter(tags=["approvals"])


class ApproveRequest(BaseModel):
    approver_id: str


@router.post("/api/approvals/{plan_id}")
async def approve_plan(plan_id: str, req: ApproveRequest, session: AsyncSession = Depends(get_session)):
    try:
        plan = await ApprovalService.approve_plan(session, plan_id, req.approver_id)
        return {"plan_id": str(plan.id), "status": plan.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Approval failed")
