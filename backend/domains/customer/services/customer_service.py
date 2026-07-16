"""Customer domain service — business orchestration layer."""

import uuid
from collections.abc import Sequence

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerStatus,
    CustomerType,
)
from domains.customer.events.customer_events import (
    CustomerActivatedEvent,
    CustomerArchivedEvent,
    CustomerCreatedEvent,
    CustomerDeactivatedEvent,
    CustomerUpdatedEvent,
    DomainEvent,
)
from domains.customer.exceptions.customer_exceptions import (
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    CustomerValidationError,
)
from domains.customer.models.customer import Customer
from domains.customer.repositories.customer_repository import CustomerRepository
from domains.customer.schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
)
from app.platform.logging import get_logger
from shared.base_service import BaseService

_ALLOWED_TRANSITIONS: dict[CustomerStatus, set[CustomerStatus]] = {
    CustomerStatus.ACTIVE: {CustomerStatus.INACTIVE, CustomerStatus.ARCHIVED},
    CustomerStatus.INACTIVE: {CustomerStatus.ACTIVE, CustomerStatus.ARCHIVED},
    CustomerStatus.SUSPENDED: {CustomerStatus.ARCHIVED},
    CustomerStatus.DECEASED: {CustomerStatus.ARCHIVED},
    CustomerStatus.ARCHIVED: set(),
}


class CustomerService(BaseService):
    def __init__(self, repository: CustomerRepository) -> None:
        self._repository = repository
        self._logger = get_logger(__name__)

    async def create_customer(
        self, data: CustomerCreateRequest
    ) -> tuple[Customer, list[DomainEvent]]:
        self._logger.info(
            "customer_create_requested", external_ref=data.external_ref
        )

        existing = await self._repository.get_by_external_ref(data.external_ref)
        if existing is not None:
            raise CustomerAlreadyExistsError(
                context={"external_ref": data.external_ref}
            )

        if data.email:
            existing_email = await self._repository.get_by_email(data.email)
            if existing_email is not None:
                raise CustomerAlreadyExistsError(
                    message="A customer with this email already exists.",
                    context={"email": data.email},
                )

        customer = await self._repository.create(**data.model_dump())
        events: list[DomainEvent] = [
            CustomerCreatedEvent(
                customer_id=customer.id, email=customer.email or ""
            )
        ]
        self._logger.info(
            "customer_created",
            customer_id=str(customer.id),
            external_ref=customer.external_ref,
        )
        return customer, events

    async def get_customer(self, customer_id: uuid.UUID) -> Customer:
        customer = await self._repository.get_by_id(customer_id)
        if customer is None or customer.is_deleted:
            raise CustomerNotFoundError(
                context={"customer_id": str(customer_id)}
            )
        return customer

    async def get_customer_by_external_ref(
        self, external_ref: str
    ) -> Customer:
        customer = await self._repository.get_by_external_ref(external_ref)
        if customer is None:
            raise CustomerNotFoundError(
                context={"external_ref": external_ref}
            )
        return customer

    async def list_customers(
        self,
        *,
        customer_type: CustomerType | None = None,
        status: CustomerStatus | None = None,
        communication_channel: CommunicationChannel | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[Customer], int]:
        self._logger.debug(
            "customer_list_requested",
            customer_type=customer_type,
            status=status,
            communication_channel=communication_channel,
            page=page,
            page_size=page_size,
        )
        return await self._repository.list(
            customer_type=customer_type,
            status=status,
            communication_channel=communication_channel,
            page=page,
            page_size=page_size,
        )

    async def update_customer(
        self, customer_id: uuid.UUID, data: CustomerUpdateRequest
    ) -> tuple[Customer, list[DomainEvent]]:
        customer = await self.get_customer(customer_id)
        self._assert_not_archived(customer)

        new_status = data.status
        if new_status is not None and new_status != customer.status:
            self._validate_customer_transition(customer.status, new_status)

        if data.email and data.email != customer.email:
            existing_email = await self._repository.get_by_email(data.email)
            if existing_email is not None and existing_email.id != customer_id:
                raise CustomerAlreadyExistsError(
                    message="A customer with this email already exists.",
                    context={"email": data.email},
                )

        updated = await self._repository.update(
            customer_id, **data.model_dump(exclude_none=True)
        )
        events: list[DomainEvent] = [
            CustomerUpdatedEvent(customer_id=customer.id)
        ]
        self._logger.info(
            "customer_updated",
            customer_id=str(customer_id),
        )
        return updated, events

    async def activate_customer(
        self, customer_id: uuid.UUID
    ) -> tuple[Customer, list[DomainEvent]]:
        customer = await self.get_customer(customer_id)
        self._assert_not_archived(customer)
        self._validate_customer_transition(customer.status, CustomerStatus.ACTIVE)

        updated = await self._repository.update(
            customer_id, status=CustomerStatus.ACTIVE
        )
        events: list[DomainEvent] = [
            CustomerActivatedEvent(customer_id=customer.id)
        ]
        self._logger.info(
            "customer_activated", customer_id=str(customer_id)
        )
        return updated, events

    async def deactivate_customer(
        self, customer_id: uuid.UUID
    ) -> tuple[Customer, list[DomainEvent]]:
        customer = await self.get_customer(customer_id)
        self._assert_not_archived(customer)
        self._validate_customer_transition(
            customer.status, CustomerStatus.INACTIVE
        )

        updated = await self._repository.update(
            customer_id, status=CustomerStatus.INACTIVE
        )
        events: list[DomainEvent] = [
            CustomerDeactivatedEvent(customer_id=customer.id)
        ]
        self._logger.info(
            "customer_deactivated", customer_id=str(customer_id)
        )
        return updated, events

    async def archive_customer(
        self, customer_id: uuid.UUID
    ) -> tuple[Customer, list[DomainEvent]]:
        customer = await self.get_customer(customer_id)
        self._assert_not_archived(customer)
        self._validate_customer_transition(
            customer.status, CustomerStatus.ARCHIVED
        )

        updated = await self._repository.update(
            customer_id, status=CustomerStatus.ARCHIVED
        )
        events: list[DomainEvent] = [
            CustomerArchivedEvent(customer_id=customer.id)
        ]
        self._logger.info(
            "customer_archived", customer_id=str(customer_id)
        )
        return updated, events

    @staticmethod
    def _assert_not_archived(customer: Customer) -> None:
        if customer.status == CustomerStatus.ARCHIVED:
            raise CustomerValidationError(
                message="Archived customers are read-only.",
                context={
                    "customer_id": str(customer.id),
                    "current_status": customer.status,
                },
            )

    @staticmethod
    def _validate_customer_transition(
        current: CustomerStatus, target: CustomerStatus
    ) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise CustomerValidationError(
                message=f"Cannot transition from '{current}' to '{target}'.",
                context={
                    "current_status": current,
                    "target_status": target,
                },
            )
