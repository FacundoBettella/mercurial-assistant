import os
from fastapi import FastAPI, Header, HTTPException

from src.middleware import (
	ModerationService,
	ModerationRequest,
	ModerationResponse,
	ModerationAction,
	JsonLogRepository,
)

app = FastAPI(title="Moderation Middleware")

log_repository = JsonLogRepository(logs_dir=os.getenv("LOGS_DIR", "logs"))

service = ModerationService(
	salt=os.getenv("LOG_HASH_SALT", "dev-salt"),
	log_repository=log_repository,
)


@app.post("/moderate", response_model=ModerationResponse)
async def moderate(
	body: ModerationRequest,
	x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> ModerationResponse:
	"""Evaluate user text for policy violations and return moderation decision."""
	request_id = x_request_id or "unknown"

	try:
		detected_risks, action, reason = service.evaluate(body.text)

		# Log the moderation event via repository
		service.log_moderation_event(
			user_id=body.user_id,
			text=body.text,
			detected_risks=detected_risks,
			action=action,
			request_id=request_id,
		)

		return ModerationResponse(
			flagged=action != ModerationAction.ALLOW,
			detected_risks=detected_risks,
			moderation_action=action,
			reason=reason,
		)
	except Exception as exc:  # pragma: no cover
		raise HTTPException(status_code=503, detail="Moderation service unavailable") from exc
