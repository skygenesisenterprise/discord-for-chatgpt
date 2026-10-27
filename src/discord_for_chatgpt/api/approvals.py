from fastapi import APIRouter

router = APIRouter(tags=["approvals"])


@router.post("/api/approvals/{plan_id}")
async def approve_plan(plan_id: str):
    return {"plan_id": plan_id, "status": "approved"}
