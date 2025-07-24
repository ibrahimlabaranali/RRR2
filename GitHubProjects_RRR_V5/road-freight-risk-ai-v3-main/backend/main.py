from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# Import routes
from routes import auth, classify, report, voice, advice

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Road Freight Risk AI API",
    description="AI-powered road freight risk reporting and safety advice system",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit local
        "https://your-streamlit-app.streamlit.app",  # Streamlit cloud
        "http://localhost:3000",  # React local
        "https://your-frontend-domain.com"  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(classify.router, prefix="/classify", tags=["Risk Classification"])
app.include_router(report.router, prefix="/reports", tags=["Risk Reports"])
app.include_router(voice.router, prefix="/voice", tags=["Voice Processing"])
app.include_router(advice.router, prefix="/advice", tags=["Safety Advice"])

# Health check endpoint
@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Road Freight Risk AI API",
        "version": "3.0.0",
        "docs": "/docs"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Road Freight Risk AI API starting up...")
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("uploads/reports", exist_ok=True)
    os.makedirs("uploads/voice", exist_ok=True)
    
    print("✅ Application startup complete")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Road Freight Risk AI API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
