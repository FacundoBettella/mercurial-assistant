from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.api.v1.routes import router as v1_router
from src.domain.exceptions import (
    ContentBlockedError,
    LLMResponseParseError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMProviderError,
    PersistenceError,
)

app = FastAPI(title="MercurIAl Assitent")


@app.exception_handler(ContentBlockedError)
async def content_blocked_handler(request: Request, exc: ContentBlockedError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.reason})


@app.exception_handler(LLMResponseParseError)
async def llm_parse_handler(request: Request, exc: LLMResponseParseError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": "The model returned an unexpected response format."})


@app.exception_handler(LLMRateLimitError)
async def llm_rate_limit_handler(request: Request, exc: LLMRateLimitError) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "Too many requests to the AI provider. Please retry later."})


@app.exception_handler(LLMTimeoutError)
async def llm_timeout_handler(request: Request, exc: LLMTimeoutError) -> JSONResponse:
    return JSONResponse(status_code=504, content={"detail": "The AI provider did not respond in time."})


@app.exception_handler(LLMProviderError)
async def llm_provider_handler(request: Request, exc: LLMProviderError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": "AI provider error."})


@app.exception_handler(PersistenceError)
async def persistence_handler(request: Request, exc: PersistenceError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Internal storage error."})


app.include_router(v1_router)
