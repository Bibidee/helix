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

Use Python 3.12 for the pinned GenLayer tooling; the CI release gate uses the same version. A Python 3.11 environment can fail before test collection because the installed SDK requires newer standard-library typing support.

```text
pytest tests/direct -q
python scripts/preflight.py
```

## Studionet deployment and v0.2.0 status

Helix v0.1.0 is the legacy documented deployment. v0.1.1 and v0.1.2 were superseded release candidates. v0.1.3 is the current historical source-matched deployment: [`0x92eD41aFC028a67857BDAF7625378E3aF431d620`](https://explorer-studio.genlayer.com/address/0x92eD41aFC028a67857BDAF7625378E3aF431d620), deployed by [transaction `0x1b7398…7082c2`](https://explorer-studio.genlayer.com/tx/0x1b7398502fd0fee14adffc28c04af09e6b12553cf1c5f9c54103af34227082c2). It finalized with GenVM `SUCCESS`; its retrieved source is byte-for-byte identical to SHA-256 `087f3220fa919a5936f046500a6a4a94c4d2dc726f008ac650d5481c4369c60a`.

v0.1.4 is historical. The local v0.2.0 hardening pass is not deployed yet. It adds a separate consumer, canonical occurrence commitments, a 32-action open quota per delegation with terminal release, a 300-second minimum challenge window, and optional hash-bound counterevidence. Validators still independently classify every safety dimension and the approval tuple remains strict; consensus compares only the deterministic derived `approved`, `blocked`, or `inconclusive` outcome. Diagnostic dimensions and rationale do not independently create consensus failure.

The following safe-path links are historical v0.1.4 evidence and do not prove v0.2.0 deployment. The v0.2.0 release record will be added only after a fresh finalized deployment and source-parity proof.

Only finalized on-chain outcomes are treated as verified live evidence. Challenge, refund, blocked, and inconclusive lifecycle protections are covered by the Direct Mode adversarial suite; this README does not claim a live Studionet outcome for any path that is not independently finalized and recorded.

Every current-deployment claim is recorded only after finalization and retrieved-source parity.
