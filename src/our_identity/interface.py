"""Public interface for our-identity.

Re-exports the primary public API types that form this brick's contract.
Consumers should import from ``our_identity`` or ``our_identity.interface``.
"""

from our_identity.did_manager import (
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
from our_identity.multi_did import (
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
