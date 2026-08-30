from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import engine
from app.api.auth import router as auth_router

app = FastAPI(
    title="Spottr API",
    version="0.1.0",
    description="Backend API for the Spottr location-based discovery application.",
)

app.include_router(auth_router)


@app.get("/health", tags=["Health"])
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected",
        }
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail="Database connection is unavailable.",
        ) from error