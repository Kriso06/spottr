from fastapi import FastAPI

app=FastAPI(
    title="Spottr API",
    version="0.1.0",
    description="Backend API"
)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}