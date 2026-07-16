"""Customer REST API — endpoints for customer profile management."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import CurrentUser, get_current_user
from app.dependencies.customer import get_customer_service
from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from domains.customer.schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerResponse,
    CustomerSummary,
    CustomerUpdateRequest,
)
from domains.customer.services.customer_service import CustomerService
from app.platform.logging import get_logger
from shared.response_schemas import PaginatedResponse, SuccessResponse

router = APIRouter(prefix="/customers", tags=["Customers"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=SuccessResponse[CustomerResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a customer",
    description="Creates a new customer profile. External reference must be unique.",
)
async def create_customer(
    body: CustomerCreateRequest,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer, _ = await service.create_customer(body)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))


@router.get(
    "",
    response_model=PaginatedResponse[CustomerSummary],
    summary="List customers",
    description="Returns a paginated list of customers with optional filters.",
)
async def list_customers(
    customer_type: CustomerType | None = Query(
        None, description="Filter by customer type"
    ),
    status: CustomerStatus | None = Query(
        None, description="Filter by status"
    ),
    communication_channel: CommunicationChannel | None = Query(
        None, description="Filter by preferred communication channel"
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> PaginatedResponse[CustomerSummary]:
    items, total = await service.list_customers(
        customer_type=customer_type,
        status=status,
        communication_channel=communication_channel,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        data=[CustomerSummary.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max(1, (total + page_size - 1) // page_size),
    )


@router.get(
    "/{customer_id}",
    response_model=SuccessResponse[CustomerResponse],
    summary="Get customer by ID",
    description="Returns a single customer profile by its unique identifier.",
)
async def get_customer(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer = await service.get_customer(customer_id)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))


@router.patch(
    "/{customer_id}",
    response_model=SuccessResponse[CustomerResponse],
    summary="Update a customer",
    description="Updates an existing customer profile. Archived customers are read-only.",
)
async def update_customer(
    customer_id: uuid.UUID,
    body: CustomerUpdateRequest,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer, _ = await service.update_customer(customer_id, body)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))


@router.post(
    "/{customer_id}/activate",
    response_model=SuccessResponse[CustomerResponse],
    summary="Activate a customer",
    description="Transitions a customer from INACTIVE to ACTIVE status.",
)
async def activate_customer(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer, _ = await service.activate_customer(customer_id)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))


@router.post(
    "/{customer_id}/deactivate",
    response_model=SuccessResponse[CustomerResponse],
    summary="Deactivate a customer",
    description="Transitions a customer from ACTIVE to INACTIVE status.",
)
async def deactivate_customer(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer, _ = await service.deactivate_customer(customer_id)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))


@router.post(
    "/{customer_id}/archive",
    response_model=SuccessResponse[CustomerResponse],
    summary="Archive a customer",
    description="Transitions a customer to ARCHIVED status. Archived customers are read-only.",
)
async def archive_customer(
    customer_id: uuid.UUID,
    service: CustomerService = Depends(get_customer_service),
    _current_user: CurrentUser | None = Depends(get_current_user),
) -> SuccessResponse[CustomerResponse]:
    customer, _ = await service.archive_customer(customer_id)
    return SuccessResponse(data=CustomerResponse.model_validate(customer))
