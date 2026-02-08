"""oro-identity — Multi-DID identity management with Ed25519 cryptography.

Each node in the network has its own DID. A user may operate multiple
nodes, grouped into an IdentityCluster. DIDs are linked via cryptographic
proofs so that compromise of one node does not endanger the others.

Key concepts:
- **DIDNode**: A single node identity with its own Ed25519 keypair.
- **IdentityCluster**: Groups multiple DIDNodes under one conceptual identity.
- **LinkProof**: Cryptographic proof that two DIDs belong to the same cluster.
- **DIDManager**: Service layer for creating, linking, revoking, and resolving DIDs.

Security properties:
- No master key / single point of failure.
- Revoking one DID does not affect others in the cluster.
- Link proofs are bidirectional (both nodes sign).
"""

__version__ = "0.1.0"

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
    "ClusterNotFoundError",
    "DIDAlreadyExistsError",
    "DIDError",
    "DIDManager",
    "DIDNode",
    "DIDNotFoundError",
    "DIDRevokedError",
    "DIDStatus",
    "DIDStore",
    "IdentityCluster",
    "InMemoryDIDStore",
    "LinkProof",
    "LinkProofInvalidError",
]
