# Helix

Helix is a standalone GenLayer delegation-scope attestor. It lets an owner issue an immutable, time-bounded delegation with semantic limits, then authorizes a hash-committed action only when independent GenLayer validators agree that the complete action artefact fits that delegation.

Helix is a reusable primitive, not an execution engine or frontend. Downstream systems must verify the committed action SHA-256 and consume an actionable attestation exactly once.

## Core lifecycle

1. An owner creates an immutable delegation: delegate, consumer, resource, purpose, constraints, exclusions, expiry, review window, and bond.
2. The delegate proposes an action using a content-addressed HTTPS manifest and evidence commitments.
3. Validators independently fetch exact raw bytes, verify SHA-256, enforce an artefact-size limit, and semantically determine whether the action is within scope.
4. Deterministic contract logic derives `approved`, `blocked`, or `inconclusive`.
5. An approval waits through a public challenge window; an independent challenger may force re-review and optionally attach hash-bound counterevidence.
6. Only an unchallenged or re-finalized approval before delegation expiry becomes actionable; only the configured consumer can consume it exactly once.

## Security invariants

- One deployable source: `contracts/helix.py`.
- Action and optional challenge artefacts are SHA-256 commitments over exact raw bytes.
- Authority, expiry, replay protection, state transitions, bond accounting, quota release, and actionability are deterministic.
- Validators independently classify the semantic dimensions; consensus compares only the deterministic derived verdict, never rationale or diagnostic-field identity.
- Approval requires the complete safe tuple plus confidence at or above the deterministic threshold; `unclear` without an affirmative unsafe finding is `INCONCLUSIVE`.
- Replay identity is `delegation_id | manifest_hash`; changing action ID, nonce, or evidence does not allow the same manifest to be registered twice within one delegation.
- Challenge sink is distinct from owner, delegate, and consumer. Owner, delegate, proposer, and consumer cannot capture the challenge round.
- Transient challenge-artifact retrieval failures are retryable and preserve the challenged state and bond. Deterministically invalid counterevidence may be slashed.
- Global pause blocks new productive execution but never strands challenge settlement or withdrawal.
- Each delegation permits at most 32 concurrent open actions. Terminal blocked, inconclusive, cancelled, or consumed actions release their slot exactly once.

## Reuse examples

- AI-agent authority: permit an agent to perform a bounded operational action without granting open-ended power.
- Multisig operations: attest that a proposed transaction batch fits a maintenance delegation.
- Treasury operations: authorize a constrained vendor payment or recurring action under a stated mandate.
- Infrastructure: authorize a dependency, model-provider, or configuration change only inside the delegated remit.

## Release gate

Use Python 3.12 for the pinned GenLayer tooling.

```text
pytest tests/direct -q
python scripts/preflight.py
```

The preflight enforces one deployable source, Direct Mode tests, GenVM lint, and ABI schema generation. `scripts/verify_source_parity.mjs` queries finalized `gen_getContractCode` and compares the retrieved bytes with `contracts/helix.py`.

## Studionet release status

The current source tree is **v0.3.1 release-candidate code and is not yet represented by a source-matched Studionet deployment**. It fixes transient-vs-invalid counterevidence handling, consumer/sink neutrality, early challenge-cancellation quota release, capacity metadata, and release-verification tooling. Do not present the v0.3.0 address below as v0.3.1 evidence.

The latest source-matched historical deployment is v0.3.0 at [`0x0bC80b70F87b493F12aBd27461666052a9FF8B57`](https://explorer-studio.genlayer.com/address/0x0bC80b70F87b493F12aBd27461666052a9FF8B57), deployed by [`0xb01c4669…148f2b`](https://explorer-studio.genlayer.com/tx/0xb01c466981a6ff19d6fb494f9d73181d167c7ff02e1fd1dafc25e41a43148f2b). Repository-recorded parity for that frozen v0.3.0 source is byte-for-byte `YES`, SHA-256 `db673f3d7e905127505d2f5dde47fab8cb6381482f50932f78e61fcca7e1b65b`.

Older v0.1.x and v0.2.0 deployments are historical only. Old `UNDETERMINED` transactions remain explorer history and are not represented as successful evidence.

A final v0.3.1 release record should be added only after: full Python 3.12 preflight, finalized deployment, retrieved-source parity, a finalized safe `APPROVED` review, a finalized clearly unsafe `BLOCKED` review, and finalized challenge/settlement evidence.
