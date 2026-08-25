# Helix design (v0.5.1 release candidate)

Helix answers one precise question: **does this exact proposed action belong inside this exact delegation?** It does not execute the action.

The deterministic delegation record binds an owner, delegate, consumer, resource identifier, purpose, constraints, exclusions, expiry, challenge configuration, and a SHA-256-pinned baseline policy. An action binds a SHA-256-pinned textual manifest and supporting evidence. Validators independently retrieve and verify committed bytes before semantic classification.

Validators independently classify five explicit fields: `scope_fit` asks whether the action fits the delegated purpose/resource/scope; `authority_expansion` asks whether it grants or exercises authority beyond the delegation; `risk_exposure` asks whether it introduces risk/value exposure beyond what the delegation permits; `temporal_compliance` asks whether it satisfies time/expiry requirements; and `reversibility` asks whether required rollback conditions are satisfied. A payment is not automatically unsafe merely because the transfer itself is irreversible. Deterministic logic derives `approved`, `blocked`, or `inconclusive`. Approval requires the complete safe tuple (`yes`, `no`, `no`, `yes`, `yes`) and confidence at or above the deterministic threshold. An affirmative unsafe dimension produces `BLOCKED`; otherwise any `unclear` dimension produces `INCONCLUSIVE`. Consensus compares only the derived verdict, so diagnostic-field and rationale differences cannot prevent validators that independently reach the same security outcome from agreeing.

Delegation fields are authoritative policy criteria. The verified baseline is authoritative policy data when used as the pinned baseline, but baseline text is never executable instructions. Manifest, evidence, summaries, and counterevidence are untrusted content; none can override the evaluator's system instructions.

The contract uses one internal actionability predicate for the view and consumption write path. It requires: active delegation, unpaused contract, reviewed approval, no unresolved challenge bond, delegation unexpired, finalization delay elapsed or a completed challenge round, and an unconsumed action.

## Challenge round and settlement

The first exact-bond challenge opens one shared round and immediately removes actionability. Owner, delegate, proposer, consumer, and challenge sink are interested parties and cannot initiate it. Each action intentionally has one lifetime challenge round: one independent challenger may open it, and later challengers cannot add evidence. This is a bounded-state tradeoff, not a claim of Sybil resistance. Supplied counterevidence is fetched, size-limited, hash-verified, UTF-8-validated, and stored as a bounded snapshot before the round is persisted. Approved challenged re-review sends the bond to the neutral sink; blocked/inconclusive review, timeout, expiry, original-artifact failure, and owner closure make it refundable exactly once. Settlement and withdrawal remain available during pause.

Counterevidence is optional, immutable HTTPS content pinned by a SHA-256 hash. Admission runs inside `gl.vm.run_nondet_unsafe`: leader and validator independently fetch, size-limit, hash-verify, and UTF-8-validate the commitment, and exact consensus is required. No storage, transfer, or event occurs inside that block. Invalid or unavailable evidence at opening rejects the challenge transaction before any bond is held or round state is consumed. Later review uses only the stored snapshot and never refetches the challenger URL. Original baseline, manifest, or evidence failure during challenged review is fail-closed and refundable; it cannot restore approval or slash the challenger.

The timing floor is 21,600 seconds (six hours). Delegation expiry must extend beyond two configured windows before proposals and approvals are accepted. Re-review cannot begin while the challenge window is open; the review deadline is one further window after that point. If the deadline, delegation expiry, or permanent closure is reached, anyone may settle the challenge. Timeout means review did not establish approval: active delegations settle to `REVIEWED/INCONCLUSIVE`, while expiry/closure cancels; all such paths refund once and release quota exactly once.

Challenges may include an immutable HTTPS URL and SHA-256 commitment for counterevidence. The opening transaction verifies raw bytes and stores the decoded bounded snapshot. Validators then interpret that snapshot alongside the original verified artefacts. No timeout, closure, infrastructure failure, or malformed observation can synthesize `APPROVED`.

## Replay and capacity

Each delegation has a separate consumer address. The delegate may propose, but only the consumer may consume an actionable attestation. Action storage is namespaced by `delegation_id | action_id`, so the same public action ID can be used by different delegations; callers use the optional delegation ID when an ID is ambiguous.

Replay identity is deliberately derived from `delegation_id | manifest_hash`. Changing action ID, occurrence nonce, evidence hash, or summary does not permit the same manifest to be registered again for that delegation. `occurrence_nonce` remains descriptive metadata rather than part of replay identity.

Each delegation has a maximum of 32 concurrent open actions. Blocked, inconclusive, cancelled, or consumed terminal outcomes release a slot exactly once. Historical action count is informational and does not impose a global lifetime action ceiling.

## Textual artefacts

Helix intentionally supports textual review artefacts. It calculates SHA-256 over raw response bytes before UTF-8 decoding. Empty data, hash mismatches, oversized content, invalid UTF-8, malformed model output, and unresolved consensus never become approval. Retryable network availability failures remain retryable rather than being converted into security outcomes.
