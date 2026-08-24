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

- One deployable source: `contracts/helix.py` (v0.4.0).
- Action and optional challenge artefacts are SHA-256 commitments over exact raw bytes.
- Authority, expiry, replay protection, state transitions, bond accounting, quota release, and actionability are deterministic.
- Validators independently classify the semantic dimensions; consensus compares only the deterministic derived verdict, never rationale or diagnostic-field identity.
- Approval requires the complete safe tuple plus confidence at or above the deterministic threshold; `unclear` without an affirmative unsafe finding is `INCONCLUSIVE`.
- Replay identity is `delegation_id | manifest_hash`; changing action ID, nonce, or evidence does not allow the same manifest to be registered twice within one delegation.
- Challenge sink is distinct from owner, delegate, and consumer. Owner, delegate, proposer, and consumer cannot capture the challenge round.
- One bounded challenge round is intentional: only one independent challenger can open it. Invalid counterevidence is slashed; if supplied counterevidence remains unavailable through the deadline, the original approval survives and the bond is slashed rather than refunded. Original-action infrastructure failures do not trigger this challenger-specific rule.
- Global pause blocks new productive execution but never strands challenge settlement or withdrawal.
- Each delegation permits at most 32 concurrent open actions. Terminal blocked, inconclusive, cancelled, or consumed actions release their slot exactly once.
- Action records are internally namespaced by `delegation_id | action_id`, so separate delegations may reuse a public action ID.

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

The working source tree is v0.4.0 and is not yet deployed. It uses a six-hour minimum challenge window, expiry validation beyond that window, and namespaced action storage. v0.3.1 is the latest historical source-matched deployment at [`0xD94f2e7c0CF068F0FF3C2bD8a95c8Cdf85A14fd2`](https://explorer-studio.genlayer.com/address/0xD94f2e7c0CF068F0FF3C2bD8a95c8Cdf85A14fd2), deployed by [`0x265c3a83f74b879ce054cee68e6740b1ed7173d34ed96b09a301738281318683`](https://explorer-studio.genlayer.com/tx/0x265c3a83f74b879ce054cee68e6740b1ed7173d34ed96b09a301738281318683). Its frozen source is commit `c36c62ca2392c8ff0564ee2958f4a4c4e2fc2f3c`, 29,950 bytes, SHA-256 `aad454d0b315879940802dfdf3659ebe74b2c1eb18eae246cebf296f2f462684`, with exact retrieved-source parity. A fresh v0.4.0 deployment is required before it can be called current.

The latest source-matched historical deployment is v0.3.0 at [`0x0bC80b70F87b493F12aBd27461666052a9FF8B57`](https://explorer-studio.genlayer.com/address/0x0bC80b70F87b493F12aBd27461666052a9FF8B57), deployed by [`0xb01c4669…148f2b`](https://explorer-studio.genlayer.com/tx/0xb01c466981a6ff19d6fb494f9d73181d167c7ff02e1fd1dafc25e41a43148f2b). Repository-recorded parity for that frozen v0.3.0 source is byte-for-byte `YES`, SHA-256 `db673f3d7e905127505d2f5dde47fab8cb6381482f50932f78e61fcca7e1b65b`.

Older v0.1.x and v0.2.0 deployments are historical only. Old `UNDETERMINED` transactions remain explorer history and are not represented as successful evidence.

Final-deployment live transactions are historical v0.3.1 evidence. Safe, blocked, inconclusive, replay, and challenge settlement outcomes for v0.4.0 remain pending until a fresh deployment and finalized state reads are available.
