# Helix design (v0.4.0 release candidate)

Helix answers one precise question: **does this exact proposed action belong inside this exact delegation?** It does not execute the action.

The deterministic delegation record binds an owner, delegate, consumer, resource identifier, purpose, constraints, exclusions, expiry, challenge configuration, and a SHA-256-pinned baseline policy. An action binds a SHA-256-pinned textual manifest and supporting evidence. Validators independently retrieve and verify committed bytes before semantic classification.

Validators independently classify five explicit fields: `scope_fit` asks whether the action fits the delegated purpose/resource/scope; `authority_expansion` asks whether it grants or exercises authority beyond the delegation; `risk_exposure` asks whether it introduces risk/value exposure beyond what the delegation permits; `temporal_compliance` asks whether it satisfies time/expiry requirements; and `reversibility` asks whether required rollback conditions are satisfied. A payment is not automatically unsafe merely because the transfer itself is irreversible. Deterministic logic derives `approved`, `blocked`, or `inconclusive`. Approval requires the complete safe tuple (`yes`, `no`, `no`, `yes`, `yes`) and confidence at or above the deterministic threshold. An affirmative unsafe dimension produces `BLOCKED`; otherwise any `unclear` dimension produces `INCONCLUSIVE`. Consensus compares only the derived verdict, so diagnostic-field and rationale differences cannot prevent validators that independently reach the same security outcome from agreeing.

Delegation fields are authoritative policy criteria. The verified baseline is authoritative policy data when used as the pinned baseline, but baseline text is never executable instructions. Manifest, evidence, summaries, and counterevidence are untrusted content; none can override the evaluator's system instructions.

The contract uses one internal actionability predicate for the view and consumption write path. It requires: active delegation, unpaused contract, reviewed approval, no unresolved challenge bond, delegation unexpired, finalization delay elapsed or a completed challenge round, and an unconsumed action.

## Challenge round and settlement

The first exact-bond challenge opens one shared round and immediately removes actionability. Owner, delegate, proposer, and consumer are interested parties and cannot initiate that round. Each action intentionally has one lifetime challenge round: one independent challenger may open it, and later challengers cannot add evidence. This is a documented bounded tradeoff, not a claim of Sybil resistance. Approved challenged re-review is final immediately and sends the bond to a neutral challenge sink that can equal neither owner, delegate, nor consumer. Blocked/inconclusive re-review makes the challenger refund available exactly once. Settlement and withdrawal remain available during contract pause.

Counterevidence is optional, immutable HTTPS content pinned by a SHA-256 hash. If supplied counterevidence is deterministically invalid, the bond is slashed. If it remains transiently unavailable through the review deadline, the challenge is treated as failed: the original approval survives, the round completes, and the bond is slashed rather than refunded. Failures affecting only the original baseline, manifest, or evidence do not trigger this challenger-specific slash path.

The timing floor is 21,600 seconds (six hours). Delegation expiry must extend beyond the configured challenge window. Re-review cannot begin while the challenge window is open; the review deadline is one further window after that point. If the deadline, delegation expiry, or permanent closure is reached, anyone may settle the challenge. A challenge with unresolved supplied counterevidence is slashed and restores the original approval; a challenge without supplied counterevidence is cancelled with a one-time refund. Every terminal path releases the per-delegation open-action quota exactly once.

Challenges may include an immutable HTTPS URL and SHA-256 commitment for counterevidence. Validators fetch and hash the raw artifact before semantic interpretation. Transient retrieval failures (`fetch_unavailable`, HTTP 408/425/429, or 5xx) are retryable and preserve `CHALLENGED` state plus the held bond. Deterministically invalid supplied counterevidence (for example hash mismatch, empty/oversized/non-UTF8 content, or a non-retryable bad HTTP response) is challenge-invalid and may slash the bond; it cannot turn a transient network outage into final approval.

## Replay and capacity

Each delegation has a separate consumer address. The delegate may propose, but only the consumer may consume an actionable attestation. Action storage is namespaced by `delegation_id | action_id`, so the same public action ID can be used by different delegations; callers use the optional delegation ID when an ID is ambiguous.

Replay identity is deliberately derived from `delegation_id | manifest_hash`. Changing action ID, occurrence nonce, evidence hash, or summary does not permit the same manifest to be registered again for that delegation. `occurrence_nonce` remains descriptive metadata rather than part of replay identity.

Each delegation has a maximum of 32 concurrent open actions. Blocked, inconclusive, cancelled, or consumed terminal outcomes release a slot exactly once. Historical action count is informational and does not impose a global lifetime action ceiling.

## Textual artefacts

Helix intentionally supports textual review artefacts. It calculates SHA-256 over raw response bytes before UTF-8 decoding. Empty data, hash mismatches, oversized content, invalid UTF-8, malformed model output, and unresolved consensus never become approval. Retryable network availability failures remain retryable rather than being converted into security outcomes.
