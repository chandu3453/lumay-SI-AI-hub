"""AI Gateway — single entry point for all AI capabilities.

Domains consume AI through this gateway only.
The gateway delegates to orchestrators, guardrails, and providers
while handling request validation, context assembly, and error handling.
"""

from ai.gateway.ai_gateway import AIGateway, AIGatewayConfig, GatewayRequest, GatewayResponse, get_ai_gateway, reset_ai_gateway

__all__ = [
    "AIGateway",
    "AIGatewayConfig",
    "GatewayRequest",
    "GatewayResponse",
    "get_ai_gateway",
    "reset_ai_gateway",
]