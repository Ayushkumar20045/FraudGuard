from typing import Optional

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    """
    User-facing FraudGuard transaction input.
    """

    # ==================================================
    # Transaction
    # ==================================================

    transaction_amount: float = Field(
        ...,
        gt=0,
        description="Transaction amount"
    )

    transaction_hour: int = Field(
        ...,
        ge=0,
        le=23,
        description="Transaction hour, 0-23"
    )

    # ==================================================
    # Product / card
    # ==================================================

    product_code: str = Field(
        ...,
        description="Product category"
    )

    card_network: str = Field(
        ...,
        description="Card network"
    )

    card_type: str = Field(
        ...,
        description="Card type"
    )

    # ==================================================
    # Address / distance
    # ==================================================

    billing_address: Optional[float] = Field(
        None,
        description="Billing address identifier"
    )

    billing_region: Optional[float] = Field(
        None,
        description="Billing region identifier"
    )

    transaction_distance: Optional[float] = Field(
        None,
        ge=0,
        description="Primary transaction distance"
    )

    secondary_distance: Optional[float] = Field(
        None,
        ge=0,
        description="Secondary transaction distance"
    )

    # ==================================================
    # Email
    # ==================================================

    purchaser_email_domain: Optional[str] = Field(
        None,
        description="Purchaser email domain"
    )

    recipient_email_domain: Optional[str] = Field(
        None,
        description="Recipient email domain"
    )

    # ==================================================
    # Device
    # ==================================================

    device_type: Optional[str] = Field(
        None,
        description="Device type"
    )

    device_info: Optional[str] = Field(
        None,
        description="Device information"
    )

    # ==================================================
    # Identity
    # ==================================================

    identity_available: bool = Field(
        False,
        description="Whether identity information is available"
    )