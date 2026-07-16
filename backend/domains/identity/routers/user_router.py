"""
Identity User Router — bootstrap only.
Registers the router prefix and tags. Business endpoints added during feature implementation.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])
