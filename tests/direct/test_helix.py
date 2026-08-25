import hashlib
import json
import pytest
import sys

from conftest import warp_to


BASELINE = "0x" + hashlib.sha256(b"baseline policy\n").hexdigest()
MANIFEST = "0x" + hashlib.sha256(b"action manifest\n").hexdigest()
EVIDENCE = "0x" + hashlib.sha256(b"evidence\n").hexdigest()
BOND = 10**18
EXPIRY = 1818720000


def deploy(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/helix.py")
    direct_vm._helix_module = sys.modules[contract.__class__.__module__]
    warp_to(direct_vm, "2026-08-24T00:00:00Z")
    return contract


def create(contract):
    contract.create_delegation("delegation-1", contract.get_info()["owner"], "payments", "settle approved invoices", "amount <= 100; vendor allowlist", "no admin rights; no transfers outside invoice", "https://example.com/baseline", BASELINE, EXPIRY, BOND, 21600)


def propose(direct_vm, contract):
    contract.propose_action("action-1", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice under the delegation limit")


def mock_review(direct_vm, **overrides):
    value = {"scope_fit": "yes", "authority_expansion": "no", "risk_exposure": "no", "temporal_compliance": "yes", "reversibility": "yes", "confidence": 90, "rationale": "The action remains inside the bounded delegation."}
    value.update(overrides)
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": value}


def test_info_and_owner_only_controls(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    assert contract.get_info()["version"] == "0.5.1"
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Owner only"):
            contract.set_paused(True)
    contract.set_paused(True)
    assert contract.get_info()["paused"]


def test_delegate_proposes_safe_action_and_consumes_once(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm)
    contract.review_action("action-1")
    assert contract.get_action("action-1")["verdict"] == "approved"
    assert not contract.is_actionable("action-1")["actionable"]
    warp_to(direct_vm, "2026-08-24T06:00:01Z")
    contract.consume_action("action-1")
    with direct_vm.expect_revert("not actionable"):
        contract.consume_action("action-1")
    assert contract.get_action("action-1")["status"] == "consumed"


@pytest.mark.parametrize("field,value", [("scope_fit", "no"), ("authority_expansion", "yes"), ("risk_exposure", "yes"), ("temporal_compliance", "no"), ("reversibility", "no")])
def test_each_semantic_safety_dimension_blocks(direct_vm, direct_deploy, field, value):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm, **{field: value})
    contract.review_action("action-1")
    assert contract.get_action("action-1")["verdict"] == "blocked"


@pytest.mark.parametrize("score,expected", [(74, "inconclusive"), (75, "approved")])
def test_confidence_threshold(direct_vm, direct_deploy, score, expected):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm, confidence=score)
    contract.review_action("action-1")
    assert contract.get_action("action-1")["verdict"] == expected


def test_unverified_or_non_text_artefacts_fail_closed(direct_vm, direct_deploy):
    deploy(direct_vm, direct_deploy); module = direct_vm._helix_module
    target, raw = "https://example.com/artefact", b"verified text\n"
    direct_vm.mock_web(target, {"status": 200, "body": raw})
    assert module.fetch_verified(target, module.content_hash(raw)) == "verified text\n"
    direct_vm.clear_mocks(); direct_vm.mock_web(target, {"status": 200, "body": raw})
    with pytest.raises(ValueError, match="hash_mismatch"): module.fetch_verified(target, "0x" + "00" * 32)
    direct_vm.clear_mocks(); direct_vm.mock_web(target, {"status": 200, "body": b"\xff"})
    with pytest.raises(ValueError, match="invalid_utf8"): module.fetch_verified(target, module.content_hash(b"\xff"))


def test_cli_numeric_hash_is_normalized_to_the_same_commitment(direct_vm, direct_deploy):
    deploy(direct_vm, direct_deploy); module = direct_vm._helix_module
    assert module.canonical_hash(int(MANIFEST, 16)) == MANIFEST


def test_different_action_id_cannot_reuse_same_occurrence_commitment(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract)
    contract.propose_action("action-1", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice", "invoice-001")
    with direct_vm.expect_revert("commitment already registered"):
        contract.propose_action("action-2", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice", "invoice-001")


def test_consumer_authorization_is_separate_from_delegate(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy)
    owner = contract.get_info()["owner"]
    contract.create_delegation("delegation-consumer", owner, "payments", "settle approved invoices", "amount <= 100", "no admin rights", "https://example.com/baseline", BASELINE, EXPIRY, BOND, 21600, direct_alice)
    contract.propose_action("action-consumer", "delegation-consumer", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice")
    mock_review(direct_vm)
    contract.review_action("action-consumer")
    warp_to(direct_vm, "2026-08-24T06:00:01Z")
    with direct_vm.expect_revert("Consumer only"):
        contract.consume_action("action-consumer")
    with direct_vm.prank(direct_alice):
        contract.consume_action("action-consumer")
    assert contract.get_action("action-consumer")["status"] == "consumed"
    assert contract.get_delegation("delegation-consumer")["consumer"].lower() == "0x" + direct_alice.hex()


def test_open_action_capacity_is_released_on_terminal_outcome(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract)
    for index in range(2):
        action_id = f"capacity-{index}"
        manifest_hash = MANIFEST if index == 0 else "0x" + "22" * 32
        contract.propose_action(action_id, "delegation-1", "https://example.com/manifest", manifest_hash, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice", f"nonce-{index}")
        direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": analysis(risk_exposure="yes", rationale="The action exceeds the delegation risk limit.")}
        contract.review_action(action_id)
    assert contract.get_delegation("delegation-1")["open_action_count"] == "0"


def test_challenge_is_a_single_protective_round_not_a_slot_race(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0
    assert contract.get_action("action-1")["status"] == "challenged"
    assert not contract.is_actionable("action-1")["actionable"]
    with direct_vm.prank(direct_bob):
        direct_vm.value = BOND
        with direct_vm.expect_revert("cannot be challenged"):
            contract.challenge_action("action-1")
    with direct_vm.expect_revert("not actionable"):
        contract.consume_action("action-1")


def test_interested_party_cannot_capture_challenge_round(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.expect_revert("Interested party"):
        contract.challenge_action("action-1")


def test_challenge_rereview_approval_slashes_to_neutral_sink(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; warp_to(direct_vm, "2026-08-24T06:00:01Z"); mock_review(direct_vm); contract.review_action("action-1")
    action = contract.get_action("action-1")
    assert action["verdict"] == "approved" and action["challenge_bond_held"] == "0" and action["challenge_settlement"] == "slashed"


def test_challenge_counterevidence_is_hash_bound_and_exposed(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    artifact = b"counter evidence\n"
    artifact_url = "https://example.com/counter-evidence"
    direct_vm.mock_web(artifact_url, {"status": 200, "body": artifact})
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        contract.challenge_action("action-1", artifact_url, "0x" + hashlib.sha256(artifact).hexdigest(), "The action exceeds the delegation boundary.")
    item = contract.get_action("action-1")
    assert item["challenge_artifact_url"] == artifact_url
    assert item["challenge_artifact_hash"] == "0x" + hashlib.sha256(artifact).hexdigest()
    assert item["challenge_summary"] == "The action exceeds the delegation boundary."
    assert item["challenge_artifact_text"] == artifact.decode()
    with direct_vm.prank(direct_alice):
        direct_vm.value = BOND
        with direct_vm.expect_revert("cannot be challenged"):
            contract.challenge_action("action-1", artifact_url, "0x" + "00" * 32, "mismatch")


def test_counterevidence_admission_runs_validator_and_rejects_changed_snapshot(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    artifact_url = "https://example.com/consensus-counter"
    artifact_a, artifact_b = b"counter A\n", b"counter B\n"
    artifact_hash = "0x" + hashlib.sha256(artifact_a).hexdigest()
    direct_vm.mock_web(artifact_url, {"status": 200, "body": artifact_a})
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        contract.challenge_action("action-1", artifact_url, artifact_hash, "Counterevidence")
    assert direct_vm.run_validator() is True
    direct_vm.clear_mocks(); direct_vm.mock_web(artifact_url, {"status": 200, "body": artifact_b})
    assert direct_vm.run_validator() is False
    item = contract.get_action("action-1")
    assert item["status"] == "challenged" and item["challenge_artifact_text"] == artifact_a.decode()


@pytest.mark.parametrize("response,expected", [
    ({"status": 404, "body": b"not found"}, "Invalid challenge evidence: bad_http_status"),
    ({"status": 200, "body": b""}, "Invalid challenge evidence: empty_response"),
    ({"status": 200, "body": bytes([255])}, "Invalid challenge evidence: invalid_utf8"),
    ({"status": 500, "body": b"temporary"}, "Challenge evidence temporarily unavailable"),
    ({"status": 429, "body": b"rate limited"}, "Challenge evidence temporarily unavailable"),
])
def test_counterevidence_admission_failures_do_not_hold_bond_or_consume_round(direct_vm, direct_deploy, direct_alice, response, expected):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    artifact_url = "https://example.com/invalid-counter"
    raw = response["body"]
    expected_hash = "0x" + hashlib.sha256(raw).hexdigest()
    direct_vm.mock_web(artifact_url, response); direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert(expected):
            contract.challenge_action("action-1", artifact_url, expected_hash, "Invalid counterevidence")
    item = contract.get_action("action-1")
    assert item["status"] == "reviewed" and item["verdict"] == "approved" and item["challenge_bond_held"] == "0"


def test_challenge_sink_cannot_open_a_round(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    sink = bytes.fromhex(contract.get_info()["challenge_sink"][2:])
    direct_vm.value = BOND
    with direct_vm.prank(sink):
        with direct_vm.expect_revert("Interested party"):
            contract.challenge_action("action-1")
    direct_vm.value = 0


def test_real_observation_pipeline_verifies_bytes_and_prompt(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    baseline = b"baseline policy\n"; manifest = b"action manifest\n"; evidence = b"evidence\n"
    direct_vm.mock_web("https://example.com/baseline", {"status": 200, "body": baseline})
    direct_vm.mock_web("https://example.com/manifest", {"status": 200, "body": manifest})
    direct_vm.mock_web("https://example.com/evidence", {"status": 200, "body": evidence})
    direct_vm.mock_llm("You review whether", json.dumps(analysis()))
    contract.review_action("action-1")
    assert contract.get_action("action-1")["verdict"] == "approved"


def test_proposal_near_expiry_is_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract)
    warp_to(direct_vm, "2027-08-19T23:00:00Z")
    with direct_vm.expect_revert("Insufficient delegation lifetime"):
        propose(direct_vm, contract)


def test_initial_approval_near_expiry_is_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    warp_to(direct_vm, "2027-08-19T23:00:00Z"); mock_review(direct_vm)
    with direct_vm.expect_revert("Insufficient delegation lifetime"):
        contract.review_action("action-1")


def test_paused_unchallenged_review_is_blocked_but_settlement_is_not(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); contract.set_paused(True)
    with direct_vm.expect_revert("Delegation unavailable"):
        contract.review_action("action-1")


def test_successful_rereview_is_final_and_cannot_be_challenged_twice(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; warp_to(direct_vm, "2026-08-24T06:00:01Z"); mock_review(direct_vm); contract.review_action("action-1")
    with direct_vm.expect_revert("cannot be challenged"):
        contract.challenge_action("action-1")
    assert contract.is_actionable("action-1")["actionable"]
    contract.consume_action("action-1")


def test_closure_during_challenge_cancels_and_refunds_once(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; contract.set_delegation_status("delegation-1", "closed")
    contract.settle_expired_challenge("action-1")
    assert contract.get_action("action-1")["status"] == "cancelled"
    with direct_vm.prank(direct_alice):
        contract.withdraw_challenge_bond("action-1")
        with direct_vm.expect_revert("No challenge refund"): contract.withdraw_challenge_bond("action-1")


def test_sink_and_public_status_guards(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    sink = "0x000000000000000000000000000000000000dEaD"
    with direct_vm.expect_revert("Delegate cannot be challenge sink"):
        contract.create_delegation("sink", sink, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21600)
    create(contract)
    with direct_vm.expect_revert("Invalid delegation status"):
        contract.set_delegation_status("delegation-1", "invalid")
    contract.set_delegation_status("delegation-1", "closed")
    with direct_vm.expect_revert("Illegal delegation transition"):
        contract.set_delegation_status("delegation-1", "active")


def test_consumed_actions_cannot_be_cancelled_or_challenged(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    warp_to(direct_vm, "2026-08-24T06:00:01Z"); contract.consume_action("action-1")
    with direct_vm.expect_revert("cannot be cancelled"): contract.cancel_action("action-1")
    with direct_vm.expect_revert("cannot be challenged"): contract.challenge_action("action-1")


def test_timeout_refund_survives_pause_and_double_withdrawal(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; contract.set_paused(True); warp_to(direct_vm, "2026-08-24T12:00:01Z")
    contract.settle_expired_challenge("action-1")
    with direct_vm.prank(direct_alice):
        contract.withdraw_challenge_bond("action-1")
        with direct_vm.expect_revert("No challenge refund"):
            contract.withdraw_challenge_bond("action-1")
    assert contract.get_action("action-1")["challenge_bond_held"] == "0"


def test_access_input_and_zero_address_guards(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    with direct_vm.expect_revert("Zero delegate"):
        contract.create_delegation("zero", "0x0000000000000000000000000000000000000000", "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21600)
    with direct_vm.expect_revert("Blocked manifest_url"):
        create(contract)
        contract.propose_action("local", "delegation-1", "https://localhost/a", MANIFEST, "https://example.com/e", EVIDENCE, "x")


def analysis(**overrides):
    value = {"scope_fit": "yes", "authority_expansion": "no", "risk_exposure": "no", "temporal_compliance": "yes", "reversibility": "yes", "confidence": 90, "rationale": "Complete bounded evaluation with a clear safety conclusion."}
    value.update(overrides)
    return value


def test_equivalence_uses_derived_verdict_for_different_blocking_dimensions(direct_vm, direct_deploy):
    deploy(direct_vm, direct_deploy); module = direct_vm._helix_module
    left = analysis(scope_fit="no", authority_expansion="yes", risk_exposure="yes", reversibility="no", confidence=95, rationale="Outside scope and expands authority.")
    right = analysis(scope_fit="no", authority_expansion="yes", risk_exposure="no", reversibility="unclear", confidence=76, rationale="Outside scope and authority is expanded.")
    assert module.verdict(left) == module.BLOCKED == module.verdict(right)
    assert module.equivalent(left, right)


def test_equivalence_preserves_approval_boundaries_and_ignores_safe_diagnostics(direct_vm, direct_deploy):
    deploy(direct_vm, direct_deploy); module = direct_vm._helix_module
    approved_low = analysis(confidence=75, rationale="Safe at the minimum deterministic confidence.")
    approved_high = analysis(confidence=100, rationale="Safe at a higher independent confidence.")
    blocked = analysis(risk_exposure="yes", rationale="Excessive value exposure blocks the action.")
    inconclusive = analysis(confidence=74, rationale="The safe tuple lacks sufficient confidence.")
    assert module.equivalent(approved_low, approved_high)
    assert not module.equivalent(approved_low, blocked)
    assert not module.equivalent(approved_low, inconclusive)
    assert not module.equivalent(blocked, {"scope_fit": "no"})


@pytest.mark.parametrize("field", ["scope_fit", "authority_expansion", "risk_exposure", "temporal_compliance", "reversibility"])
def test_unclear_without_affirmative_unsafe_is_inconclusive(direct_vm, direct_deploy, field):
    deploy(direct_vm, direct_deploy); module = direct_vm._helix_module
    value = analysis(**{field: "unclear"})
    assert module.verdict(value) == module.INCONCLUSIVE


def test_manifest_hash_is_replay_identity_even_when_nonce_or_evidence_changes(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract)
    contract.propose_action("identity-1", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay invoice", "nonce-a")
    different_evidence = "0x" + "11" * 32
    with direct_vm.expect_revert("commitment already registered"):
        contract.propose_action("identity-2", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/other", different_evidence, "Pay invoice", "nonce-b")


def test_unsafe_evidence_consensus_regression_blocks_when_diagnostics_differ(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    module = direct_vm._helix_module
    leader = analysis(scope_fit="no", authority_expansion="yes", risk_exposure="yes", reversibility="no", confidence=95, rationale="Unsafe manifest requests permanent administrative withdrawal authority.")
    validator = analysis(scope_fit="no", authority_expansion="yes", risk_exposure="no", reversibility="unclear", confidence=82, rationale="Unsafe manifest is outside the constrained payment delegation.")
    assert module.equivalent(leader, validator)
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": validator}
    contract.review_action("action-1")
    assert contract.get_action("action-1")["verdict"] == "blocked"


def _capture_review(contract, direct_vm, leader_result):
    direct_vm.clear_validators()
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": leader_result}
    contract.review_action("action-1")


def test_validator_specific_approved_vs_blocked_is_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    _capture_review(contract, direct_vm, analysis())
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": analysis(scope_fit="no", rationale="Outside scope.")}
    assert direct_vm.run_validator() is False


def test_validator_specific_approved_vs_inconclusive_is_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    _capture_review(contract, direct_vm, analysis())
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": analysis(confidence=74, rationale="Insufficient confidence.")}
    assert direct_vm.run_validator() is False


def test_validator_specific_blocked_diagnostic_disagreement_is_accepted(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    leader = analysis(scope_fit="no", authority_expansion="yes", risk_exposure="yes", rationale="Scope and authority violation.")
    _capture_review(contract, direct_vm, leader)
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": analysis(scope_fit="no", authority_expansion="yes", risk_exposure="no", reversibility="unclear", confidence=76, rationale="Scope violation only.")}
    assert direct_vm.run_validator() is True


def test_validator_specific_approved_confidence_disagreement_is_accepted(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    _capture_review(contract, direct_vm, analysis(confidence=75, rationale="Minimum safe confidence."))
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": analysis(confidence=95, rationale="Higher safe confidence.")}
    assert direct_vm.run_validator() is True


def test_validator_specific_artifact_availability_disagreement_is_rejected(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract)
    _capture_review(contract, direct_vm, analysis())
    direct_vm._helix_module.observe = lambda *args: {"kind": "observation_error", "class": "fetch_unavailable"}
    assert direct_vm.run_validator() is False
