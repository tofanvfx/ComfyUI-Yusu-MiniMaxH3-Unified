from __future__ import annotations

import asyncio
import logging

from aiohttp import web
from server import PromptServer

from .media import (
    MAX_UPLOAD_BYTES,
    resolve_media_path,
    validate_upload_name,
    validate_uploaded_file,
)
from .nodes import comfy_entrypoint

WEB_DIRECTORY = "./web"
LOGGER = logging.getLogger(__name__)


async def inspect_media(request: web.Request) -> web.Response:
    try:
        body = await request.json()
        if not isinstance(body, dict):
            raise ValueError("Media inspect request must be a JSON object")
        relative_path = str(body.get("path", ""))
        expected_kind = str(body.get("kind", ""))
        mime = str(body.get("mime", ""))
        path = resolve_media_path(relative_path)
        size = path.stat().st_size
        if size > MAX_UPLOAD_BYTES:
            return web.json_response({"error": "File exceeds the 512 MiB limit"}, status=413)
        _extension, kind = validate_upload_name(path.name, mime)
        if expected_kind != kind:
            raise ValueError(f"Slot requires {expected_kind or 'unknown'}, but uploaded {kind}")
        metadata = await asyncio.to_thread(validate_uploaded_file, path, kind)
        return web.json_response(
            {
                "path": relative_path,
                "kind": kind,
                "size": size,
                **metadata,
            }
        )
    except (ValueError, OSError, web.HTTPException) as error:
        return web.json_response({"error": str(error)}, status=400)
    except Exception:
        LOGGER.exception("Unexpected error during MiniMax H3 media inspect")
        return web.json_response({"error": "Media inspect failed, please check ComfyUI console logs"}, status=500)


server_instance = getattr(PromptServer, "instance", None)
if server_instance is not None:
    server_instance.routes.post("/minimax_h3_unified/inspect")(inspect_media)


__all__ = ["WEB_DIRECTORY", "comfy_entrypoint"]
