import numpy as np
import pandas as pd

from api.schemas import TransactionInput


def build_model_row(
    transaction: TransactionInput,
) -> pd.DataFrame:
    """
    Convert user-facing transaction information into the
    raw FraudGuard feature representation.

    Only meaningful user-provided values are populated.
    Missing model features are explicitly represented as
    NaN so the existing FraudGuard preprocessing pipeline
    can handle them consistently.
    """

    row = {
        # ==================================================
        # Core transaction
        # ==================================================

        "TransactionAmt": transaction.transaction_amount,

        "TransactionDT": (
            transaction.transaction_hour
            * 60
            * 60
        ),

        # ==================================================
        # Product / card
        # ==================================================

        "ProductCD": transaction.product_code,

        "card4": transaction.card_network,

        "card6": transaction.card_type,

        # ==================================================
        # Address / distance
        # ==================================================

        "addr1": transaction.billing_address,

        "addr2": transaction.billing_region,

        "dist1": transaction.transaction_distance,

        "dist2": transaction.secondary_distance,

        # ==================================================
        # Email
        # ==================================================

        "P_emaildomain": (
            transaction.purchaser_email_domain
        ),

        "R_emaildomain": (
            transaction.recipient_email_domain
        ),

        # ==================================================
        # Device
        # ==================================================

        "DeviceType": transaction.device_type,

        "DeviceInfo": transaction.device_info,

        # ==================================================
        # Identity
        # ==================================================

        "id_01": (
            1.0
            if transaction.identity_available
            else np.nan
        ),

        # ==================================================
        # M-series signals
        #
        # These are not exposed to the user yet.
        # Explicit NaN prevents feature-engineering
        # failures while preserving missingness.
        # ==================================================

        "M1": np.nan,
        "M2": np.nan,
        "M3": np.nan,
        "M4": np.nan,
        "M5": np.nan,
        "M6": np.nan,
        "M7": np.nan,
        "M8": np.nan,
        "M9": np.nan,
    }

    return pd.DataFrame([row])