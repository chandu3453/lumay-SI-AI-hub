"""Audit API router — bootstrap. Endpoints added during feature implementation."""

from fastapi import APIRouter

router = APIRouter(prefix="/audit", tags=["Audit"])
