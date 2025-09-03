# FastAPI app entrypoint
# This file will contain the main FastAPI application setup 

from fastapi import FastAPI
from routes import api

app = FastAPI(title="Trading Bot")
app.include_router(api.router, prefix="/api")