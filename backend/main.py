"""
Thamarat ERP - نظام محاسبة المنظمات الإنسانية
Desktop Edition
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from models.database import engine, Base, get_db
from models import *  # Import all models
from routes import auth, accounts, journal, funds, budget, reports, audit
from utils.config import settings
from utils.license import LicenseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('thamarat.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Initialize license manager
license_manager = LicenseManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting Thamarat ERP Desktop Edition...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized")
    
    # Check license
    if not license_manager.is_valid():
        logger.warning("⚠️ Running in trial mode")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Thamarat ERP...")

# Create FastAPI app
app = FastAPI(
    title="Thamarat ERP",
    description="نظام محاسبة المنظمات الإنسانية - Humanitarian Accounting System",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["المصادقة"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["شجرة الحسابات"])
app.include_router(journal.router, prefix="/api/journal", tags=["القيود المحاسبية"])
app.include_router(funds.router, prefix="/api/funds", tags=["الصناديق"])
app.include_router(budget.router, prefix="/api/budget", tags=["الميزانيات"])
app.include_router(reports.router, prefix="/api/reports", tags=["التقارير"])
app.include_router(audit.router, prefix="/api/audit", tags=["التدقيق"])

@app.get("/")
async def root():
    return {
        "name": "Thamarat ERP",
        "version": "1.0.0",
        "edition": "Desktop",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "license": "valid" if license_manager.is_valid() else "trial"
    }

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 5000))
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info"
    )
