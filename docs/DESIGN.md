# Helix design

Helix answers one precise question: **does this exact proposed action belong inside this exact delegation?** It does not execute the action.

The deterministic delegation record binds an owner, delegate, resource identifier, purpose, constraints, exclusions, expiry, challenge configuration, and a SHA-256-pinned baseline policy. An action binds a SHA-256-pinned textual action manifest and supporting evidence. Validators independently retrieve and verify committed bytes before semantic classification.

The initial semantic dimensions will be scope fit, authority expansion, value/risk exposure, temporal compliance, and reversibility. Approval requires exact categorical agreement on these dimensions plus a deterministic confidence threshold. Rationale remains explanatory only.

The contract will use one internal actionability predicate for the view and consumption write path. It will require: active delegation, unpaused contract, reviewed approval, no unresolved challenge bond, delegation unexpired, finalization delay elapsed, and unconsumed action.

## Challenge round and settlement

The first exact-bond challenge opens one shared round and immediately removes actionability. There is no challenger list and no finite set of challenge slots to occupy. The review may occur only once the original challenge window closes; anyone can trigger it. Approved re-review sends the bond to a neutral configured sink, never to the owner or delegate. A blocked/inconclusive re-review or deadline timeout makes the challenger refund available exactly once. Settlement and withdrawal remain available during contract pause or delegation closure.

## Textual artefacts

Helix intentionally supports textual review artefacts. It calculates SHA-256 over raw response bytes before UTF-8 decoding. Empty data, hash mismatches, oversized content, invalid UTF-8, HTTP errors, malformed model output, and consensus disagreement fail closed.
