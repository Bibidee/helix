import hashlib
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
    contract.create_delegation("delegation-1", contract.get_info()["owner"], "payments", "settle approved invoices", "amount <= 100; vendor allowlist", "no admin rights; no transfers outside invoice", "https://example.com/baseline", BASELINE, EXPIRY, BOND, 60)


def propose(direct_vm, contract):
    contract.propose_action("action-1", "delegation-1", "https://example.com/manifest", MANIFEST, "https://example.com/evidence", EVIDENCE, "Pay a verified invoice under the delegation limit")


def mock_review(direct_vm, **overrides):
    value = {"scope_fit": "yes", "authority_expansion": "no", "risk_exposure": "no", "temporal_compliance": "yes", "reversibility": "yes", "confidence": 90, "rationale": "The action remains inside the bounded delegation."}
    value.update(overrides)
    direct_vm._helix_module.observe = lambda *args: {"kind": "analysis", "result": value}


def test_info_and_owner_only_controls(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    assert contract.get_info()["version"] == "0.1.3"
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
    warp_to(direct_vm, "2026-08-24T00:01:01Z")
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


def test_challenge_is_a_single_protective_round_not_a_slot_race(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0
    assert contract.get_action("action-1")["status"] == "challenged"
    assert not contract.is_actionable("action-1")["actionable"]
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert("cannot be challenged"):
            contract.challenge_action("action-1")
    with direct_vm.expect_revert("not actionable"):
        contract.consume_action("action-1")


def test_challenge_rereview_approval_slashes_to_neutral_sink(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; warp_to(direct_vm, "2026-08-24T00:01:01Z"); mock_review(direct_vm); contract.review_action("action-1")
    action = contract.get_action("action-1")
    assert action["verdict"] == "approved" and action["challenge_bond_held"] == "0" and action["challenge_settlement"] == "slashed"


def test_successful_rereview_is_final_and_cannot_be_challenged_twice(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; warp_to(direct_vm, "2026-08-24T00:01:01Z"); mock_review(direct_vm); contract.review_action("action-1")
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
        contract.create_delegation("sink", sink, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 60)
    create(contract)
    with direct_vm.expect_revert("Invalid delegation status"):
        contract.set_delegation_status("delegation-1", "invalid")
    contract.set_delegation_status("delegation-1", "closed")
    with direct_vm.expect_revert("Illegal delegation transition"):
        contract.set_delegation_status("delegation-1", "active")


def test_consumed_actions_cannot_be_cancelled_or_challenged(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    warp_to(direct_vm, "2026-08-24T00:01:01Z"); contract.consume_action("action-1")
    with direct_vm.expect_revert("cannot be cancelled"): contract.cancel_action("action-1")
    with direct_vm.expect_revert("cannot be challenged"): contract.challenge_action("action-1")


def test_timeout_refund_survives_pause_and_double_withdrawal(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy); create(contract); propose(direct_vm, contract); mock_review(direct_vm); contract.review_action("action-1")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice): contract.challenge_action("action-1")
    direct_vm.value = 0; contract.set_paused(True); warp_to(direct_vm, "2026-08-24T00:02:01Z")
    contract.settle_expired_challenge("action-1")
    with direct_vm.prank(direct_alice):
        contract.withdraw_challenge_bond("action-1")
        with direct_vm.expect_revert("No challenge refund"):
            contract.withdraw_challenge_bond("action-1")
    assert contract.get_action("action-1")["challenge_bond_held"] == "0"


def test_access_input_and_zero_address_guards(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    with direct_vm.expect_revert("Zero delegate"):
        contract.create_delegation("zero", "0x0000000000000000000000000000000000000000", "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 60)
    with direct_vm.expect_revert("Blocked manifest_url"):
        create(contract)
        contract.propose_action("local", "delegation-1", "https://localhost/a", MANIFEST, "https://example.com/e", EVIDENCE, "x")
