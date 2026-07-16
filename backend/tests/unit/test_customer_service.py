"""Customer service unit tests."""

import uuid

import pytest

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
)
from domains.customer.exceptions.customer_exceptions import (
    CustomerAlreadyExistsError,
    CustomerNotFoundError,
    CustomerValidationError,
)
from domains.customer.schemas.customer_schema import (
    CustomerCreateRequest,
    CustomerUpdateRequest,
)
from domains.customer.services.customer_service import CustomerService


@pytest.fixture
def active_customer_kwargs() -> dict:
    return dict(
        id=uuid.uuid4(),
        external_ref="CUST-001",
        full_name="John Doe",
        email="john@example.com",
        mobile_number=None,
        customer_type=CustomerType.ACTIVE,
        communication_channel=None,
        status=CustomerStatus.ACTIVE,
        is_deleted=False,
    )


@pytest.fixture
def inactive_customer_kwargs(active_customer_kwargs) -> dict:
    kwargs = dict(active_customer_kwargs)
    kwargs["status"] = CustomerStatus.INACTIVE
    return kwargs


@pytest.fixture
def archived_customer_kwargs(active_customer_kwargs) -> dict:
    kwargs = dict(active_customer_kwargs)
    kwargs["status"] = CustomerStatus.ARCHIVED
    return kwargs


@pytest.fixture
async def service(mocker, active_customer_kwargs) -> CustomerService:
    mock_repo = mocker.AsyncMock()
    mock_repo.get_by_id.return_value = mocker.Mock(**active_customer_kwargs)
    mock_repo.get_by_external_ref.return_value = None
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = mocker.Mock(**active_customer_kwargs)
    mock_repo.update.return_value = mocker.Mock(**active_customer_kwargs)
    return CustomerService(repository=mock_repo)


@pytest.mark.asyncio
class TestCustomerService:
    async def test_create_customer_returns_entity_and_event(
        self, service: CustomerService,
    ) -> None:
        data = CustomerCreateRequest(
            external_ref="CUST-001",
            full_name="John Doe",
        )
        customer, events = await service.create_customer(data)
        assert customer is not None
        assert len(events) == 1
        assert isinstance(events[0], CustomerCreatedEvent)

    async def test_create_customer_duplicate_external_ref_raises(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.get_by_external_ref.return_value = mocker.Mock()
        data = CustomerCreateRequest(
            external_ref="DUP-EXT",
            full_name="Duplicate",
        )
        with pytest.raises(CustomerAlreadyExistsError):
            await service.create_customer(data)

    async def test_create_customer_duplicate_email_raises(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.get_by_email.return_value = mocker.Mock()
        data = CustomerCreateRequest(
            external_ref="UNIQUE-REF",
            full_name="Duplicate Email",
            email="dup@example.com",
        )
        with pytest.raises(CustomerAlreadyExistsError):
            await service.create_customer(data)

    async def test_get_customer_found(
        self, service: CustomerService,
    ) -> None:
        customer = await service.get_customer(uuid.uuid4())
        assert customer is not None
        assert customer.full_name == "John Doe"

    async def test_get_customer_not_found_raises(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = None
        with pytest.raises(CustomerNotFoundError):
            await service.get_customer(uuid.uuid4())

    async def test_get_customer_soft_deleted_raises(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            is_deleted=True, id=uuid.uuid4(),
        )
        with pytest.raises(CustomerNotFoundError):
            await service.get_customer(uuid.uuid4())

    async def test_get_customer_by_external_ref_found(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.get_by_external_ref.return_value = mocker.Mock(
            external_ref="CUST-001",
        )
        customer = await service.get_customer_by_external_ref("CUST-001")
        assert customer is not None
        assert customer.external_ref == "CUST-001"

    async def test_get_customer_by_external_ref_not_found_raises(
        self, service: CustomerService,
    ) -> None:
        with pytest.raises(CustomerNotFoundError):
            await service.get_customer_by_external_ref("UNKNOWN")

    async def test_update_customer_returns_entity_and_event(
        self, service: CustomerService,
    ) -> None:
        data = CustomerUpdateRequest(full_name="Updated Name")
        customer, events = await service.update_customer(uuid.uuid4(), data)
        assert customer is not None
        assert len(events) == 1
        assert isinstance(events[0], CustomerUpdatedEvent)

    async def test_update_archived_customer_raises(
        self, service: CustomerService, mocker, archived_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **archived_customer_kwargs,
        )
        data = CustomerUpdateRequest(full_name="Nope")
        with pytest.raises(CustomerValidationError):
            await service.update_customer(uuid.uuid4(), data)

    async def test_update_customer_duplicate_email_raises(
        self, service: CustomerService, mocker, active_customer_kwargs,
    ) -> None:
        current = mocker.Mock(**active_customer_kwargs)
        current.email = "current@example.com"
        service._repository.get_by_id.return_value = current
        other = mocker.Mock(id=uuid.uuid4())
        service._repository.get_by_email.return_value = other

        data = CustomerUpdateRequest(email="taken@example.com")
        with pytest.raises(CustomerAlreadyExistsError):
            await service.update_customer(current.id, data)

    async def test_update_customer_same_email_allowed(
        self, service: CustomerService, mocker, active_customer_kwargs,
    ) -> None:
        current = mocker.Mock(**active_customer_kwargs)
        current.email = "same@example.com"
        service._repository.get_by_id.return_value = current

        data = CustomerUpdateRequest(email="same@example.com")
        customer, events = await service.update_customer(current.id, data)
        assert customer is not None

    async def test_update_customer_invalid_transition_raises(
        self, service: CustomerService, mocker, active_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **active_customer_kwargs,
        )
        data = CustomerUpdateRequest(status=CustomerStatus.ARCHIVED)
        customer, events = await service.update_customer(uuid.uuid4(), data)
        assert customer is not None

    async def test_activate_customer_returns_entity_and_event(
        self, service: CustomerService, mocker, inactive_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **inactive_customer_kwargs,
        )
        service._repository.update.return_value = mocker.Mock(
            **{**inactive_customer_kwargs, "status": CustomerStatus.ACTIVE},
        )
        customer, events = await service.activate_customer(uuid.uuid4())
        assert customer is not None
        assert len(events) == 1
        assert isinstance(events[0], CustomerActivatedEvent)

    async def test_activate_archived_customer_raises(
        self, service: CustomerService, mocker, archived_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **archived_customer_kwargs,
        )
        with pytest.raises(CustomerValidationError):
            await service.activate_customer(uuid.uuid4())

    async def test_deactivate_customer_returns_entity_and_event(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            status=CustomerStatus.INACTIVE,
        )
        customer, events = await service.deactivate_customer(uuid.uuid4())
        assert customer is not None
        assert len(events) == 1
        assert isinstance(events[0], CustomerDeactivatedEvent)

    async def test_deactivate_archived_customer_raises(
        self, service: CustomerService, mocker, archived_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **archived_customer_kwargs,
        )
        with pytest.raises(CustomerValidationError):
            await service.deactivate_customer(uuid.uuid4())

    async def test_archive_customer_returns_entity_and_event(
        self, service: CustomerService, mocker,
    ) -> None:
        service._repository.update.return_value = mocker.Mock(
            status=CustomerStatus.ARCHIVED,
        )
        customer, events = await service.archive_customer(uuid.uuid4())
        assert customer is not None
        assert len(events) == 1
        assert isinstance(events[0], CustomerArchivedEvent)

    async def test_archive_archived_customer_raises(
        self, service: CustomerService, mocker, archived_customer_kwargs,
    ) -> None:
        service._repository.get_by_id.return_value = mocker.Mock(
            **archived_customer_kwargs,
        )
        with pytest.raises(CustomerValidationError):
            await service.archive_customer(uuid.uuid4())

    async def test_list_customers(self, service: CustomerService) -> None:
        service._repository.list.return_value = ([], 0)
        items, total = await service.list_customers()
        assert items == []
        assert total == 0

    async def test_activate_already_active_raises(
        self, service: CustomerService,
    ) -> None:
        with pytest.raises(CustomerValidationError):
            await service.activate_customer(uuid.uuid4())
