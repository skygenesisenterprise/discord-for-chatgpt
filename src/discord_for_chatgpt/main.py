from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .api import health, oauth, approvals
from .mcp.server import mcp_app


def create_app() -> FastAPI:
    app = FastAPI(
        title="Discord for ChatGPT",
        description="Discord integration for ChatGPT via MCP",
        version="0.1.0",
    )

    app.include_router(health.router)
    app.include_router(oauth.router)
    app.include_router(approvals.router)
    app.mount("/mcp", mcp_app)

    @app.get("/")
    async def root():
        return JSONResponse({"name": "discord-for-chatgpt", "version": "0.1.0"})

    return app


app = create_app()
