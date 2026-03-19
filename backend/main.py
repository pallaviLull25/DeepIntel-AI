import asyncio
import ast
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, Union

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse

from backend.models import ResearchApiResponse, ResearchRequest
from backend.research_service import perform_research

load_dotenv(".env.local")
load_dotenv()

logger = logging.getLogger(__name__)
app = FastAPI()
is_production = os.getenv("NODE_ENV") == "production"
dist_dir = Path(__file__).resolve().parent.parent / "dist"


def _get_error_status(error: Exception) -> int:
    for attr_name in ("status", "status_code", "code"):
        status = getattr(error, attr_name, None)
        if isinstance(status, int):
            return status

    match = re.match(r"(\d{3})\b", str(error))
    if match:
        return int(match.group(1))

    return 500


def _get_error_message(error: Exception) -> str:
    message = str(error)
    payload = None

    try:
        payload = json.loads(message)
    except json.JSONDecodeError:
        payload_start = message.find("{")
        if payload_start != -1:
            try:
                payload = ast.literal_eval(message[payload_start:])
            except (SyntaxError, ValueError):
                payload = None

    if isinstance(payload, dict):
        nested_error = payload.get("error")
        if isinstance(nested_error, dict):
            nested_message = nested_error.get("message")
            if isinstance(nested_message, str) and nested_message.strip():
                return nested_message

    return message


@app.get("/api/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "mode": "production" if is_production else "development"}


@app.post("/api/research", response_model=ResearchApiResponse)
async def research(request: ResearchRequest) -> Union[ResearchApiResponse, JSONResponse]:
    topic = request.topic.strip()
    if not topic:
        return JSONResponse(status_code=400, content={"error": "Topic is required."})

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return JSONResponse(status_code=500, content={"error": "GEMINI_API_KEY is not configured on the server."})

    try:
        return await asyncio.to_thread(perform_research, topic, api_key, request.context)
    except Exception as error:  # noqa: BLE001
        logger.exception("Research request failed")
        return JSONResponse(
            status_code=_get_error_status(error),
            content={"error": _get_error_message(error)},
        )


if is_production and dist_dir.exists():
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        candidate = (dist_dir / full_path).resolve()

        if full_path and candidate.is_file() and dist_dir in candidate.parents:
            return FileResponse(candidate)

        return FileResponse(dist_dir / "index.html")
