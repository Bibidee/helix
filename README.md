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

- One deployable source: `contracts/helix.py` (v0.5.0).
- Action and optional challenge artefacts are SHA-256 commitments over exact raw bytes.
- Authority, expiry, replay protection, state transitions, bond accounting, quota release, and actionability are deterministic.
- Validators independently classify the semantic dimensions; consensus compares only the deterministic derived verdict, never rationale or diagnostic-field identity.
- Approval requires the complete safe tuple plus confidence at or above the deterministic threshold; `unclear` without an affirmative unsafe finding is `INCONCLUSIVE`.
- Replay identity is `delegation_id | manifest_hash`; changing action ID, nonce, or evidence does not allow the same manifest to be registered twice within one delegation.
- Challenge sink is distinct from owner, delegate, and consumer. Owner, delegate, proposer, and consumer cannot capture the challenge round.
- One bounded lifetime challenge round is intentional: only one independent challenger can open it. Counterevidence is fetched, hash-verified, UTF-8-validated, and snapshotted at opening, so later URL availability is irrelevant. Invalid opening evidence rejects the transaction without consuming the round or holding a bond. Original-artifact failure, timeout, expiry, and owner closure never manufacture approval and never slash an unresolved challenger; they produce a non-actionable outcome and a one-time refund.
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

The Direct Mode suite includes genuine validator-specific divergence checks via `direct_vm.run_validator()`: approval/block disagreement, approval/inconclusive disagreement, blocked diagnostic disagreement, confidence-only approval disagreement, and artifact-availability disagreement. These tests do not alter the frozen deployable source.

## Studionet release status

The v0.4.0 deployment is historical at [`0xfB191c351c51B20d0A84F2B1363b0e151300704E`](https://explorer-studio.genlayer.com/address/0xfB191c351c51B20d0A84F2B1363b0e151300704E). The current v0.5.0 deployment is [`0xDEB91F9682C4F89980CdCD059c89A2148d11D819`](https://explorer-studio.genlayer.com/address/0xDEB91F9682C4F89980CdCD059c89A2148d11D819), deployed by [`0x01966b9980881cec81a2b95455c99c5a6c093dfb0ff6c1278eafe23eec1f09d1`](https://explorer-studio.genlayer.com/tx/0x01966b9980881cec81a2b95455c99c5a6c093dfb0ff6c1278eafe23eec1f09d1). The finalized deployment source is commit `e6a13d9`, 31,365 bytes, SHA-256 `695cfc1ed2c969159e00d4bd775d2a41aac84edca6033ca8307ba381149346b6`; retrieved-source parity is byte-for-byte `YES`.

The latest source-matched historical deployment is v0.3.0 at [`0x0bC80b70F87b493F12aBd27461666052a9FF8B57`](https://explorer-studio.genlayer.com/address/0x0bC80b70F87b493F12aBd27461666052a9FF8B57), deployed by [`0xb01c4669…148f2b`](https://explorer-studio.genlayer.com/tx/0xb01c466981a6ff19d6fb494f9d73181d167c7ff02e1fd1dafc25e41a43148f2b). Repository-recorded parity for that frozen v0.3.0 source is byte-for-byte `YES`, SHA-256 `db673f3d7e905127505d2f5dde47fab8cb6381482f50932f78e61fcca7e1b65b`.

Older v0.1.x and v0.2.0 deployments are historical only. Old `UNDETERMINED` transactions remain explorer history and are not represented as successful evidence.

Recorded v0.4.0 live evidence: delegation [`0x02e72d9e90be1b316a1a0c5ef7b090cc530dd8712fc4f63664591df17cfadb61`](https://explorer-studio.genlayer.com/tx/0x02e72d9e90be1b316a1a0c5ef7b090cc530dd8712fc4f63664591df17cfadb61); safe proposal [`0x1da7087cbf4d19d7eeaea8f5aaf43c8c70eb0fc3b9cb025bb6fd576a701c320d`](https://explorer-studio.genlayer.com/tx/0x1da7087cbf4d19d7eeaea8f5aaf43c8c70eb0fc3b9cb025bb6fd576a701c320d) and review [`0x3a72f4fb018008c0c6207992dd4a93d9deabd1e9db800b014eb0fefd9c9ca7e7`](https://explorer-studio.genlayer.com/tx/0x3a72f4fb018008c0c6207992dd4a93d9deabd1e9db800b014eb0fefd9c9ca7e7) finalized `approved`; unsafe proposal [`0xb1c1952d8ee6aa9da9689c948a64b35edef20598052b11a361f9963c1af33800`](https://explorer-studio.genlayer.com/tx/0xb1c1952d8ee6aa9da9689c948a64b35edef20598052b11a361f9963c1af33800) and review [`0xf4cb2cf0a30fc971bbf19b5081aa2f93c6472c857ba4c9f5b71daba0261d423d`](https://explorer-studio.genlayer.com/tx/0xf4cb2cf0a30fc971bbf19b5081aa2f93c6472c857ba4c9f5b71daba0261d423d) finalized `blocked`; replay [`0xae91e2000ab9153c9a59b313b2030fce9d999ef9055fbae34b68e34b23fd025a`](https://explorer-studio.genlayer.com/tx/0xae91e2000ab9153c9a59b313b2030fce9d999ef9055fbae34b68e34b23fd025a) finalized with `[EXPECTED] Action commitment already registered`; inconclusive proposal [`0xf16e30ba4aebcf88efea4e5adb5fe85501e3bbdcaef86b329de7fec535de84be`](https://explorer-studio.genlayer.com/tx/0xf16e30ba4aebcf88efea4e5adb5fe85501e3bbdcaef86b329de7fec535de84be) and review [`0xfcba757925a9b9e22ecf5904bd1a481fe0ef52267dfbb354d8daea251c89f38d`](https://explorer-studio.genlayer.com/tx/0xfcba757925a9b9e22ecf5904bd1a481fe0ef52267dfbb354d8daea251c89f38d) finalized `reviewed / inconclusive` at confidence 10; valid bonded challenge [`0xcc7878e06b750c9a288a571b79673603589e7b5474623201ad5f3249504ded3b`](https://explorer-studio.genlayer.com/tx/0xcc7878e06b750c9a288a571b79673603589e7b5474623201ad5f3249504ded3b) finalized with challenger `0xae82EFfe54dCcfd170d9a08EeE128339A70347f7`, bond `0.001 GEN`, state `challenged`, and `challenge_bond_held = 1000000000000000`.

Recorded v0.5.0 live evidence: deployment `0xDEB91F9682C4F89980CdCD059c89A2148d11D819`; safe review [`0x6a168b65f22ed8afd100451d49734d7b1e37f6268eb727d2db59bf46e7446759`](https://explorer-studio.genlayer.com/tx/0x6a168b65f22ed8afd100451d49734d7b1e37f6268eb727d2db59bf46e7446759) finalized `approved`; unsafe review [`0x649bec17a66e775d81336c45f8ac78078fe65054d98661ce0f321db19d4e163f`](https://explorer-studio.genlayer.com/tx/0x649bec17a66e775d81336c45f8ac78078fe65054d98661ce0f321db19d4e163f) finalized `blocked`; ambiguous review [`0xf1641abb42b7c01f4db8dc9bfba277a00246f7ad3d7a6d87f25986f85df3af3f`](https://explorer-studio.genlayer.com/tx/0xf1641abb42b7c01f4db8dc9bfba277a00246f7ad3d7a6d87f25986f85df3af3f) finalized `inconclusive`; replay [`0x6e8b2603da9a70c8d6470d61645a75f4c8db3a1da8c1319cd26d19ed0e339159`](https://explorer-studio.genlayer.com/tx/0x6e8b2603da9a70c8d6470d61645a75f4c8db3a1da8c1319cd26d19ed0e339159) finalized with the expected replay rollback; payable challenge [`0x30499eb2407a5a81a06555504b4465f69f5b5edb649f8fb37bae605bb003cae0`](https://explorer-studio.genlayer.com/tx/0x30499eb2407a5a81a06555504b4465f69f5b5edb649f8fb37bae605bb003cae0) finalized and left `safe-v050` challenged with a `0.001 GEN` bond held. The challenged re-review and independent consumption remain protocol-time-gated.

### Design tradeoffs and future hardening

Helix intentionally permits one lifetime challenge round per action to keep challenge state and economics bounded and deterministic. Counterevidence is snapshotted at opening. A timeout, original-artifact failure, expiry, or owner closure never creates `APPROVED`; it ends in a non-actionable outcome and refunds the held challenger bond. A successful challenged semantic review that returns `APPROVED` sends the bond to the neutral sink; `BLOCKED` or `INCONCLUSIVE` makes it refundable. Multi-watchdog aggregation is outside v0.5.0 scope.

Challenge periods are measured from deterministic GenLayer transaction timestamps, not guaranteed wall-clock time after explorer finalization. Consensus/finality latency can reduce externally observed time; deployments should choose operational margin above the six-hour minimum.
