from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.v1.routes import router as v1_router
from src.domain.exceptions import ContentBlockedError

app = FastAPI(title="MercurIAl Assitent")

@app.exception_handler(ContentBlockedError)
async def content_blocked_handler(request: Request, exc: ContentBlockedError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.reason})

app.include_router(v1_router)
