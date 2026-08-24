# Helix design (v0.3.1 release candidate)

Helix answers one precise question: **does this exact proposed action belong inside this exact delegation?** It does not execute the action.

The deterministic delegation record binds an owner, delegate, consumer, resource identifier, purpose, constraints, exclusions, expiry, challenge configuration, and a SHA-256-pinned baseline policy. An action binds a SHA-256-pinned textual manifest and supporting evidence. Validators independently retrieve and verify committed bytes before semantic classification.

Validators independently classify scope fit, authority expansion, value/risk exposure, temporal compliance, and reversibility. Deterministic logic derives `approved`, `blocked`, or `inconclusive`. Approval requires the complete safe tuple (`yes`, `no`, `no`, `yes`, `yes`) and confidence at or above the deterministic threshold. An affirmative unsafe dimension produces `BLOCKED`; otherwise any `unclear` dimension produces `INCONCLUSIVE`. Consensus compares only the derived verdict, so diagnostic-field and rationale differences cannot prevent validators that independently reach the same security outcome from agreeing.

The contract uses one internal actionability predicate for the view and consumption write path. It requires: active delegation, unpaused contract, reviewed approval, no unresolved challenge bond, delegation unexpired, finalization delay elapsed or a completed challenge round, and an unconsumed action.

## Challenge round and settlement

The first exact-bond challenge opens one shared round and immediately removes actionability. Owner, delegate, proposer, and consumer are interested parties and cannot initiate that round. Each action has exactly one lifetime challenge round. Approved challenged re-review is final immediately and sends the bond to a neutral challenge sink that can equal neither owner, delegate, nor consumer. Blocked/inconclusive, timeout, permanent delegation closure, or delegation expiry make the challenger refund available exactly once. Settlement and withdrawal remain available during contract pause.

The timing floor is 300 seconds. Re-review cannot begin while the challenge window is open; the review deadline is one further window after that point. If the deadline, delegation expiry, or permanent closure is reached, anyone may cancel the challenged action and the challenger can withdraw exactly once. Every cancellation path releases the per-delegation open-action quota exactly once.

Challenges may include an immutable HTTPS URL and SHA-256 commitment for counterevidence. Validators fetch and hash the raw artifact before semantic interpretation. Transient retrieval failures (`fetch_unavailable`, HTTP 408/425/429, or 5xx) are retryable and preserve `CHALLENGED` state plus the held bond. Deterministically invalid supplied counterevidence (for example hash mismatch, empty/oversized/non-UTF8 content, or a non-retryable bad HTTP response) is challenge-invalid and may slash the bond; it cannot turn a transient network outage into final approval.

## Replay and capacity

Each delegation has a separate consumer address. The delegate may propose, but only the consumer may consume an actionable attestation.

Replay identity is deliberately derived from `delegation_id | manifest_hash`. Changing action ID, occurrence nonce, evidence hash, or summary does not permit the same manifest to be registered again for that delegation. `occurrence_nonce` remains descriptive metadata rather than part of replay identity.

Each delegation has a maximum of 32 concurrent open actions. Blocked, inconclusive, cancelled, or consumed terminal outcomes release a slot exactly once. Historical action count is informational and does not impose a global lifetime action ceiling.

## Textual artefacts

Helix intentionally supports textual review artefacts. It calculates SHA-256 over raw response bytes before UTF-8 decoding. Empty data, hash mismatches, oversized content, invalid UTF-8, malformed model output, and unresolved consensus never become approval. Retryable network availability failures remain retryable rather than being converted into security outcomes.
