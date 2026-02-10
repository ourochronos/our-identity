# our-identity

Decentralized multi-DID identity management with Ed25519 cryptography for the ourochronos ecosystem.

## Overview

our-identity implements a decentralized identity system where each node has its own DID (Decentralized Identifier) backed by an Ed25519 keypair. Multiple DIDs can be grouped into an **IdentityCluster** to represent a single user across devices or contexts. There is no master key — compromising one node doesn't endanger others. Linking is proven through bilateral signatures (both parties must sign).

## Install

```bash
pip install our-identity
```

Requires `cryptography>=42.0` for Ed25519 operations.

## Usage

```python
from our_identity import DIDManager

mgr = DIDManager()

# Create node identities
laptop, laptop_key = mgr.create_node_did(label="laptop")
phone, phone_key = mgr.create_node_did(label="phone")

# Link them (requires both private keys — bilateral proof)
proof = mgr.link_dids(laptop.did, laptop_key, phone.did, phone_key)

# Verify the link proof offline
assert mgr.verify_link_proof(proof)

# Resolve identity from any member DID
cluster = mgr.resolve_identity(laptop.did)
assert len(cluster.nodes) == 2

# Revoke a compromised node (others unaffected)
mgr.revoke_did(phone.did, reason="key compromised")
cluster = mgr.resolve_identity(laptop.did)
assert len(cluster.nodes) == 1  # laptop still active
```

### Cluster Merging

```python
# Two separate clusters merge automatically when cross-linked
mgr.link_dids(a.did, a_key, b.did, b_key)  # cluster 1
mgr.link_dids(c.did, c_key, d.did, d_key)  # cluster 2
mgr.link_dids(b.did, b_key, c.did, c_key)  # merges into one cluster
```

### Pluggable Storage

```python
# Default: in-memory (for tests)
mgr = DIDManager()

# Custom backend: implement the DIDStore protocol
mgr = DIDManager(store=MyPostgresStore())
```

## API

| Class | Description |
|-------|-------------|
| `DIDManager` | High-level service: create, link, revoke, resolve, verify |
| `DIDNode` | A single node identity with Ed25519 keypair and status |
| `IdentityCluster` | Group of linked DIDs representing one conceptual identity |
| `LinkProof` | Bilateral cryptographic proof that two DIDs belong together |
| `DIDStore` | Protocol for pluggable storage backends |
| `InMemoryDIDStore` | Default in-memory implementation |
| `DIDStatus` | Enum: `ACTIVE`, `REVOKED`, `SUSPENDED` |

### Key Properties

- **DIDs are deterministic**: derived from Ed25519 public key fingerprint (`did:valence:<fingerprint>`)
- **Bilateral linking**: both parties must sign to establish a link
- **Revocation isolation**: revoking one DID leaves other cluster members unaffected
- **Offline verification**: link proofs can be verified without an external authority

## Development

```bash
# Install with dev dependencies
make dev

# Run linters
make lint

# Run tests
make test

# Run tests with coverage
make test-cov

# Auto-format
make format
```

## State Ownership

Owns DID nodes, identity clusters, and link proofs. Default storage is in-memory; persistent backends store to the injected `DIDStore` implementation.

## Part of Valence

This brick is part of the [Valence](https://github.com/ourochronos/valence) knowledge substrate. See [our-infra](https://github.com/ourochronos/our-infra) for ourochronos conventions.

## License

MIT
