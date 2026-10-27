import asyncio
from datetime import datetime, timedelta

from discord_for_chatgpt.services.approvals import ApprovalService


def test_plan_hash_stable():
    data = {"action": "send_message", "parameters": {"content": "hi"}}
    h1 = ApprovalService.compute_plan_hash(data)
    h2 = ApprovalService.compute_plan_hash(dict(sorted(data.items())))
    assert h1 == h2
