"""FastAPI endpoints for FactMarrow"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI(
    title="FactMarrow API",
    description="Multi-Agent Analysis of Public Health Documents",
    version="0.1.0-alpha"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0-alpha"}

@app.post("/api/analyze")
async def analyze_document(file: UploadFile = File(...)):
    """Submit document for analysis"""
    # Placeholder for document analysis workflow
    return {
        "status": "Analysis queued",
        "file": file.filename,
        "message": "Document will be analyzed by FactMarrow agents"
    }

@app.get("/api/analyses")
async def list_analyses():
    """List all analyses"""
    return {"analyses": [], "total": 0}

@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: int):
    """Get specific analysis"""
    raise HTTPException(status_code=404, detail="Analysis not found")
