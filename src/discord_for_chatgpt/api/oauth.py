from fastapi import APIRouter

router = APIRouter(tags=["oauth"])


@router.get("/oauth/discord/start")
async def start():
    return {"url": "https://discord.com/oauth2/authorize"}


@router.get("/oauth/discord/callback")
async def callback():
    return {"status": "ok"}
