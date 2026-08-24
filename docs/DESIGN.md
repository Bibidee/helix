# Helix design

Helix answers one precise question: **does this exact proposed action belong inside this exact delegation?** It does not execute the action.

The deterministic delegation record binds an owner, delegate, resource identifier, purpose, constraints, exclusions, expiry, challenge configuration, and a SHA-256-pinned baseline policy. An action binds a SHA-256-pinned textual action manifest and supporting evidence. Validators independently retrieve and verify committed bytes before semantic classification.

Validators independently classify scope fit, authority expansion, value/risk exposure, temporal compliance, and reversibility. Deterministic logic derives `approved`, `blocked`, or `inconclusive` from that classification. Approval requires the complete safe tuple (`yes`, `no`, `no`, `yes`, `yes`) and confidence at or above the deterministic threshold. Consensus compares only this derived verdict: diagnostic-field and rationale differences cannot prevent validators that independently reach `blocked` from agreeing, while `approved` never equals either `blocked` or `inconclusive`.

The contract will use one internal actionability predicate for the view and consumption write path. It will require: active delegation, unpaused contract, reviewed approval, no unresolved challenge bond, delegation unexpired, finalization delay elapsed, and unconsumed action.

## Challenge round and settlement

The first exact-bond challenge opens one shared round and immediately removes actionability. There is no challenger list and no finite set of challenge slots to occupy. Each action has exactly one lifetime challenge round. After challenged re-review, whether it approves, blocks, or is inconclusive, another challenge is rejected. Approved re-review is final immediately, with no second challenge delay, and sends the bond to a neutral sink that can equal neither owner nor delegate. Blocked/inconclusive, timeout, permanent delegation closure, or delegation expiry make the challenger refund available exactly once. Settlement and withdrawal remain available during contract pause.

The v0.2.0 timing floor is 300 seconds. Re-review cannot begin while the challenge window is open; the review deadline is one further window after that point. If the deadline, delegation expiry, or permanent closure is reached, anyone may cancel the challenged action and the challenger can withdraw exactly once. A funded challenge remains reviewable while paused, but a new unchallenged review does not proceed while paused or inactive.

Each delegation has a separate consumer address. The delegate may propose, but only the consumer may consume an actionable attestation. Every open action consumes one per-delegation quota slot; blocked, inconclusive, cancelled, or consumed terminal outcomes release it exactly once. The canonical commitment prevents the same delegation occurrence and artefact hashes being proposed again under a different action ID.

Challenges may include an immutable HTTPS URL and SHA-256 commitment for counterevidence. Validators fetch and hash that raw artifact before semantic interpretation; omitted counterevidence is valid, but a supplied mismatch fails closed.

## Textual artefacts

Helix intentionally supports textual review artefacts. It calculates SHA-256 over raw response bytes before UTF-8 decoding. Empty data, hash mismatches, oversized content, invalid UTF-8, HTTP errors, malformed model output, and consensus disagreement fail closed.
