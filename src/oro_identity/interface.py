"""Public interface for oro-identity.

Re-exports the primary public API types that form this brick's contract.
Consumers should import from ``oro_identity`` or ``oro_identity.interface``.
"""

from oro_identity.did_manager import (
    ClusterNotFoundError,
    DIDAlreadyExistsError,
    DIDError,
    DIDManager,
    DIDNotFoundError,
    DIDRevokedError,
    DIDStore,
    InMemoryDIDStore,
    LinkProofInvalidError,
)
from oro_identity.multi_did import (
    DIDNode,
    DIDStatus,
    IdentityCluster,
    LinkProof,
)

__all__ = [
    # Service
    "DIDManager",
    # Models
    "DIDNode",
    "DIDStatus",
    "IdentityCluster",
    "LinkProof",
    # Storage
    "DIDStore",
    "InMemoryDIDStore",
    # Errors
    "DIDError",
    "DIDAlreadyExistsError",
    "DIDNotFoundError",
    "DIDRevokedError",
    "ClusterNotFoundError",
    "LinkProofInvalidError",
]
