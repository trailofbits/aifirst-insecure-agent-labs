"""
FastAPI main application
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.chat import router as chat_router
from api.admin import router as admin_router
from api.employee import router as employee_router
from api.models import HealthResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Chatbot Framework API",
    description="API for prompt injection testing chatbot",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chatbot Framework API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        guardrails_available=True
    )


# Include routers
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(admin_router, tags=["admin"])  # Internal admin endpoints (Lab 2: SSRF)
app.include_router(employee_router, tags=["employee"])  # Employee data endpoints (Lab 4: IDOR)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
