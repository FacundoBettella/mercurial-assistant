from fastapi import FastAPI

from src.api.v1.routes import router as v1_router


app = FastAPI(title="MercurIAl Assitent")

# Register all v1 routes
app.include_router(v1_router)
