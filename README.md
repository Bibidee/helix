# Helix

Helix is a standalone GenLayer delegation-scope attestor. It lets an owner issue an immutable, time-bounded delegation with semantic limits, then authorizes a hash-committed action only when independent GenLayer validators agree that the complete action artefact fits that delegation.

Helix is a reusable primitive, not an execution engine or frontend. Downstream systems must verify the committed action SHA-256 and consume an actionable attestation exactly once.

## Core lifecycle

1. An owner creates an immutable delegation: delegate, resource, purpose, constraints, exclusions, expiry, review window, and bond.
2. The delegate proposes an action using a content-addressed HTTPS action artefact and SHA-256 commitment.
3. Validators independently fetch exact raw bytes, verify SHA-256, enforce a strict artefact-size limit, and semantically determine whether the action is within scope.
4. Deterministic contract logic derives `approved`, `blocked`, or `inconclusive`.
5. An approval waits through a public challenge window; a challenge forces re-review and has a deterministic bond settlement route.
6. Only an unchallenged or re-finalized approval before delegation expiry becomes actionable; consuming it prevents replay.

## Security invariants

- One deployable source: `contracts/helix.py`.
- Action artefacts are SHA-256 commitments over exact raw bytes, decoded and reviewed in full only when within the explicit size limit.
- Authority, expiry, replay protection, state transitions, bond accounting, and actionability are deterministic.
- Semantic dimensions are independently observed and compared categorically; rationale is not an equivalence input.
- Failed fetching, integrity mismatch, malformed model output, and disagreement never become approval.
- Global pause blocks new productive execution but never strands challenge settlement or withdrawal.

## Reuse examples

- AI-agent authority: permit an agent to perform a bounded operational action without granting open-ended power.
- Multisig operations: attest that a proposed transaction batch fits a maintenance delegation.
- Treasury operations: authorize a constrained vendor payment or recurring action under a stated mandate.
- Infrastructure: authorize a dependency, model-provider, or configuration change only inside the delegated remit.

## Release gate

The package includes Direct Mode adversarial tests, portable preflight, GenVM lint discovery, and ABI schema generation. Tests are outside `contracts/`, so test-only imports cannot be detected as deployable contract sources.

```text
pytest tests/direct -q
python scripts/preflight.py
```

## Studionet deployment

Helix v0.1.0 is deployed at [`0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732`](https://explorer-studio.genlayer.com/address/0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732). Deployment transaction [`0x92b9…cb4b0a`](https://explorer-studio.genlayer.com/tx/0x92b9cab4228f684f5d7406869b5447f801f59dca49da8aa3f4bbf271f8cb4b0a) finalized with majority agreement and GenVM execution `SUCCESS`.

The deployed source was retrieved independently after finalization. Its SHA-256 and the local `contracts/helix.py` SHA-256 are both `40a561e42421ec6e4f13d63748c4b5c64849893f86a1bab023f35a6c1e4a0c89`; the 23,331-character sources match byte-for-byte.
