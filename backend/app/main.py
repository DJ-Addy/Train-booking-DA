from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import engine, Base, init_db
from .routers import analytics

# Create database tables
init_db()

app = FastAPI(
    title="Train Booking System API",
    version="1.0.0",
    description="API for train ticket booking system with analytics"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# TODO: more routers to implement:
# app.include_router(stations.router, prefix="/api/stations", tags=["Stations"])
# app.include_router(journeys.router, prefix="/api/journeys", tags=["Journeys"])
# app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])

@app.get("/")
def read_root():
    return {
        "message": "Train Booking System API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "analytics": "/api/analytics"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)