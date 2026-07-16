"""Customer ORM model — Customer domain."""

from sqlalchemy import JSON, Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from domains.customer.constants.customer_constants import (
    CommunicationChannel,
    CustomerSegment,
    CustomerStatus,
    CustomerType,
)
from shared.base_model import AuditModel, SoftDeleteMixin


class Customer(AuditModel, SoftDeleteMixin):
    __tablename__ = "customers"

    customer_number: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    external_ref: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, index=True
    )
    mobile_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    communication_channel: Mapped[CommunicationChannel | None] = mapped_column(
        SAEnum(
            CommunicationChannel,
            name="communication_channel",
            create_constraint=True,
        ),
        nullable=True,
    )
    customer_type: Mapped[CustomerType] = mapped_column(
        SAEnum(CustomerType, name="customer_type", create_constraint=True),
        nullable=False,
        default=CustomerType.ACTIVE,
    )
    segment: Mapped[CustomerSegment] = mapped_column(
        SAEnum(CustomerSegment, name="customer_segment", create_constraint=True),
        nullable=False,
        default=CustomerSegment.INDIVIDUAL,
    )
    status: Mapped[CustomerStatus] = mapped_column(
        SAEnum(CustomerStatus, name="customer_status", create_constraint=True),
        nullable=False,
        default=CustomerStatus.ACTIVE,
        index=True,
    )
    profile_metadata: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
