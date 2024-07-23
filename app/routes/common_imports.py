# Centralizes the imports I will need for all routes
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db

# __all__ contains all public modules imported with a wildcard import of
# imports.py
__all__ = ["APIRouter", "Depends", "HTTPException", "status", "get_db", "AsyncIOMotorDatabase"]
