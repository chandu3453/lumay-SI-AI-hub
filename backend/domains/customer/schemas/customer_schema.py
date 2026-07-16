"""Customer Pydantic schemas — Customer domain."""

import uuid
from datetime import datetime

from pydantic import EmailStr, Field

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from shared.base_schema import AppBaseModel, EntitySchema


class CustomerCreateRequest(AppBaseModel):
    external_ref: str = Field(min_length=1, max_length=100)
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr | None = None
    mobile_number: str | None = Field(default=None, max_length=50)
    customer_type: CustomerType = CustomerType.ACTIVE
    communication_channel: CommunicationChannel | None = None
    segment: str = "individual"


class CustomerUpdateRequest(AppBaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    mobile_number: str | None = Field(default=None, max_length=50)
    customer_type: CustomerType | None = None
    communication_channel: CommunicationChannel | None = None
    segment: str | None = None
    status: CustomerStatus | None = None


class CustomerResponse(EntitySchema):
    external_ref: str
    full_name: str
    email: str | None
    mobile_number: str | None
    customer_type: CustomerType
    communication_channel: CommunicationChannel | None
    segment: str
    status: CustomerStatus


class CustomerSummary(AppBaseModel):
    id: uuid.UUID
    external_ref: str
    full_name: str
    email: str | None = None
    customer_type: CustomerType
    communication_channel: CommunicationChannel | None
    segment: str
    status: CustomerStatus
    created_at: datetime
