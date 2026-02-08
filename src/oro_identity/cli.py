"""CLI commands for multi-DID identity management.

Implements ``identity {list,link,revoke}`` commands.

Uses the modular registration pattern — the ``register_identity_commands``
function attaches the subparser to the main CLI and the ``cmd_identity``
handler dispatches to the correct sub-command.
"""

from __future__ import annotations

import argparse
import json
import sys

from oro_identity.did_manager import (
    DIDError,
    DIDManager,
    DIDNotFoundError,
    InMemoryDIDStore,
)

# ---------------------------------------------------------------------------
# Persistent store helpers
# ---------------------------------------------------------------------------

_DEFAULT_STORE_PATH = "~/.valence/identity_store.json"


def _load_manager(store_path: str | None = None) -> tuple[DIDManager, InMemoryDIDStore]:
    """Load a DIDManager backed by a JSON file store.

    Returns (manager, store) so callers can persist after mutations.
    """
    import os
    from pathlib import Path

    from oro_identity.multi_did import DIDNode, IdentityCluster, LinkProof

    path = Path(os.path.expanduser(store_path or _DEFAULT_STORE_PATH))
    store = InMemoryDIDStore()

    if path.exists():
        with open(path) as f:
            data = json.load(f)
        for node_data in data.get("nodes", []):
            store.save_node(DIDNode.from_dict(node_data))
        for cluster_data in data.get("clusters", []):
            cluster = IdentityCluster.from_dict(cluster_data)
            store.save_cluster(cluster)
        for proof_data in data.get("proofs", []):
            store.save_proof(LinkProof.from_dict(proof_data))

    return DIDManager(store=store), store


def _save_store(store: InMemoryDIDStore, store_path: str | None = None) -> None:
    """Persist the in-memory store to JSON."""
    import os
    from pathlib import Path

    path = Path(os.path.expanduser(store_path or _DEFAULT_STORE_PATH))
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "nodes": [n.to_dict() for n in store._nodes.values()],
        "clusters": [c.to_dict() for c in store._clusters.values()],
        "proofs": [p.to_dict() for p in store._proofs],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


def _cmd_identity_list(args: argparse.Namespace) -> int:
    """List all registered DIDs and clusters."""
    mgr, _store = _load_manager(getattr(args, "store", None))

    nodes = mgr.list_nodes()
    clusters = mgr.list_clusters()

    if getattr(args, "json", False):
        print(
            json.dumps(
                {
                    "nodes": [n.to_dict() for n in nodes],
                    "clusters": [c.to_dict() for c in clusters],
                },
                indent=2,
            )
        )
        return 0

    if not nodes:
        print("No DIDs registered.")
        return 0

    print(f"{'DID':<45} {'Label':<15} {'Status':<10} {'Cluster'}")
    print("\u2500" * 95)
    for node in nodes:
        cluster_label = ""
        if node.cluster_id:
            cluster = mgr.resolve_identity(node.did)
            if cluster:
                cluster_label = cluster.label or node.cluster_id[:8]
        status_icon = "\U0001f7e2" if node.is_active else "\U0001f534"
        print(f"{node.did:<45} {node.label:<15} {status_icon} {node.status.value:<7} {cluster_label}")

    if clusters:
        print(f"\n\U0001f4e6 {len(clusters)} cluster(s), {len(nodes)} DID(s) total")

    return 0


def _cmd_identity_link(args: argparse.Namespace) -> int:
    """Link two DIDs into the same identity cluster."""
    print(
        "\u26a0\ufe0f  Linking requires access to both private keys.\n"
        "   Use the Python API (DIDManager.link_dids) for programmatic linking.\n"
        "   This command verifies an existing link proof.",
        file=sys.stderr,
    )

    mgr, _store = _load_manager(getattr(args, "store", None))

    did_a = args.did_a
    did_b = args.did_b

    try:
        node_a = _store.get_node(did_a)
        node_b = _store.get_node(did_b)
    except Exception:
        node_a = node_b = None

    if node_a is None:
        print(f"\u274c DID not found: {did_a}", file=sys.stderr)
        return 1
    if node_b is None:
        print(f"\u274c DID not found: {did_b}", file=sys.stderr)
        return 1

    # Show current cluster status
    cluster_a = mgr.resolve_identity(did_a)
    cluster_b = mgr.resolve_identity(did_b)

    if cluster_a and cluster_b and cluster_a.cluster_id == cluster_b.cluster_id:
        print(f"\u2705 Both DIDs already in cluster: {cluster_a.label or cluster_a.cluster_id}")
        return 0

    print(f"DID A: {did_a} (cluster: {cluster_a.cluster_id[:8] if cluster_a else 'none'})")
    print(f"DID B: {did_b} (cluster: {cluster_b.cluster_id[:8] if cluster_b else 'none'})")
    print("\nTo link programmatically:")
    print(f"  mgr.link_dids('{did_a}', key_a, '{did_b}', key_b)")

    return 0


def _cmd_identity_revoke(args: argparse.Namespace) -> int:
    """Revoke a compromised DID."""
    mgr, store = _load_manager(getattr(args, "store", None))

    did = args.did
    reason = getattr(args, "reason", "") or ""

    try:
        node = mgr.revoke_did(did, reason=reason)
    except DIDNotFoundError:
        print(f"\u274c DID not found: {did}", file=sys.stderr)
        return 1

    _save_store(store, getattr(args, "store", None))
    print(f"\U0001f534 Revoked: {node.did} ({node.label})")
    if reason:
        print(f"   Reason: {reason}")

    return 0


# ---------------------------------------------------------------------------
# Command dispatch
# ---------------------------------------------------------------------------


def cmd_identity(args: argparse.Namespace) -> int:
    """Dispatch to the correct identity sub-command."""
    sub = getattr(args, "identity_command", None)

    dispatch = {
        "list": _cmd_identity_list,
        "link": _cmd_identity_link,
        "revoke": _cmd_identity_revoke,
    }

    if not isinstance(sub, str):
        print("Usage: identity {list,link,revoke}", file=sys.stderr)
        return 1

    handler = dispatch.get(sub)
    if handler is None:
        print("Usage: identity {list,link,revoke}", file=sys.stderr)
        return 1

    try:
        return handler(args)
    except DIDError as exc:
        print(f"\u274c {exc}", file=sys.stderr)
        return 1


# ---------------------------------------------------------------------------
# Modular registration
# ---------------------------------------------------------------------------


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register ``identity`` sub-commands on a CLI parser.

    Called from a main CLI to wire up the identity commands.
    """
    identity_parser = subparsers.add_parser(
        "identity",
        help="Multi-DID identity management",
    )
    identity_subparsers = identity_parser.add_subparsers(
        dest="identity_command",
        required=True,
    )

    # identity list
    list_parser = identity_subparsers.add_parser("list", help="List all DIDs and clusters")
    list_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    list_parser.add_argument("--store", help="Path to identity store file")

    # identity link
    link_parser = identity_subparsers.add_parser(
        "link",
        help="Show link status between two DIDs",
    )
    link_parser.add_argument("did_a", help="First DID")
    link_parser.add_argument("did_b", help="Second DID")
    link_parser.add_argument("--store", help="Path to identity store file")

    # identity revoke
    revoke_parser = identity_subparsers.add_parser(
        "revoke",
        help="Revoke a compromised DID",
    )
    revoke_parser.add_argument("did", help="DID to revoke")
    revoke_parser.add_argument("--reason", "-r", help="Reason for revocation")
    revoke_parser.add_argument("--store", help="Path to identity store file")

    identity_parser.set_defaults(func=cmd_identity)


# Backward-compatible alias
register_identity_commands = register
