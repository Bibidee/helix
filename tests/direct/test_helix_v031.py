import hashlib
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


def create(contract, consumer=""):
    contract.create_delegation(
        "delegation-v031",
        contract.get_info()["owner"],
        "payments",
        "settle approved invoices",
        "amount <= 100; vendor allowlist",
        "no admin rights; no transfers outside invoice",
        "https://example.com/baseline",
        BASELINE,
        EXPIRY,
        BOND,
        21600,
        consumer,
    )


def propose(contract):
    contract.propose_action(
        "action-v031",
        "delegation-v031",
        "https://example.com/manifest",
        MANIFEST,
        "https://example.com/evidence",
        EVIDENCE,
        "Pay a verified invoice under the delegation limit",
    )


def approved():
    return {
        "kind": "analysis",
        "result": {
            "scope_fit": "yes",
            "authority_expansion": "no",
            "risk_exposure": "no",
            "temporal_compliance": "yes",
            "reversibility": "yes",
            "confidence": 90,
            "rationale": "The action remains inside the bounded delegation.",
        },
    }


def open_challenge(direct_vm, contract, challenger):
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    with direct_vm.prank(challenger):
        contract.challenge_action("action-v031")
    direct_vm.value = 0
    warp_to(direct_vm, "2026-08-24T06:00:01Z")


def test_v031_consumer_cannot_equal_challenge_sink(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    sink = contract.get_info()["challenge_sink"]
    with direct_vm.expect_revert("Consumer cannot be challenge sink"):
        create(contract, sink)


def test_v031_consumer_is_an_interested_party_for_challenges(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract, direct_alice)
    propose(contract)
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Interested party"):
            contract.challenge_action("action-v031")
    direct_vm.value = 0


def test_v050_original_artifact_failure_is_inconclusive_and_refundable(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        contract.challenge_action("action-v031")
    direct_vm.value = 0
    warp_to(direct_vm, "2026-08-24T06:00:01Z")
    direct_vm._helix_module.observe = lambda *args: {"kind": "observation_error", "class": "fetch_unavailable"}
    contract.review_action("action-v031")
    action = contract.get_action("action-v031")
    assert action["status"] == "reviewed"
    assert action["verdict"] == "inconclusive"
    assert action["challenge_bond_held"] == str(BOND)
    assert action["challenge_settlement"] == "refund"


def test_v050_invalid_counterevidence_is_rejected_before_opening(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    artifact_url = "https://example.com/counter"
    direct_vm.mock_web(artifact_url, {"status": 200, "body": b"counter"})
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("Invalid challenge evidence"):
            contract.challenge_action("action-v031", artifact_url, "0x" + "11" * 32, "counter")
    action = contract.get_action("action-v031")
    assert action["status"] == "reviewed"
    assert action["verdict"] == "approved"
    assert action["challenge_bond_held"] == "0"
    assert action["challenge_settlement"] == ""


def test_v050_timeout_never_approves_and_refunds(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    artifact = b"counter"
    artifact_url = "https://example.com/counter"
    direct_vm.mock_web(artifact_url, {"status": 200, "body": artifact})
    with direct_vm.prank(direct_alice):
        contract.challenge_action("action-v031", artifact_url, "0x" + hashlib.sha256(artifact).hexdigest(), "counter")
    direct_vm.value = 0
    warp_to(direct_vm, "2026-08-24T12:00:01Z")
    contract.settle_expired_challenge("action-v031")
    action = contract.get_action("action-v031")
    assert action["status"] == "reviewed"
    assert action["verdict"] == "inconclusive"
    assert action["challenge_bond_held"] == str(BOND)
    assert action["challenge_settlement"] == "refund"
    with direct_vm.prank(direct_alice):
        contract.withdraw_challenge_bond("action-v031")
    assert contract.get_action("action-v031")["challenge_bond_held"] == "0"


def test_v031_early_closed_challenge_cancellation_releases_capacity(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    direct_vm._helix_module.observe = lambda *args: approved()
    contract.review_action("action-v031")
    direct_vm.value = BOND
    with direct_vm.prank(direct_alice):
        contract.challenge_action("action-v031")
    direct_vm.value = 0
    contract.set_delegation_status("delegation-v031", "closed")
    contract.review_action("action-v031")
    assert contract.get_action("action-v031")["status"] == "cancelled"
    assert contract.get_delegation("delegation-v031")["open_action_count"] == "0"


def test_v031_capacity_metadata_matches_enforced_limits(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    info = contract.get_info()
    assert info["version"] == "0.5.0"
    assert info["capacity"] == {"delegations": 128, "open_actions_per_delegation": 32}


def test_v040_window_floor_and_expiry_guard(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    owner = contract.get_info()["owner"]
    with direct_vm.expect_revert("Invalid delegation configuration"):
        contract.create_delegation("too-short", owner, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21599)
    contract.create_delegation("exact-floor", owner, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21600)
    with direct_vm.expect_revert("Invalid delegation configuration"):
        contract.create_delegation("expires-too-soon", owner, "r", "p", "c", "e", "https://example.com/base", BASELINE, 1787551200, BOND, 21600)


def test_v040_action_ids_are_namespaced_by_delegation(direct_vm, direct_deploy):
    contract = deploy(direct_vm, direct_deploy)
    owner = contract.get_info()["owner"]
    contract.create_delegation("namespace-a", owner, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21600)
    contract.create_delegation("namespace-b", owner, "r", "p", "c", "e", "https://example.com/base", BASELINE, EXPIRY, BOND, 21600)
    contract.propose_action("same-id", "namespace-a", "https://example.com/manifest-a", MANIFEST, "https://example.com/evidence-a", EVIDENCE, "a")
    contract.propose_action("same-id", "namespace-b", "https://example.com/manifest-b", MANIFEST, "https://example.com/evidence-b", EVIDENCE, "b")
    assert contract.get_action("same-id", "namespace-a")["delegation_id"] == "namespace-a"
    assert contract.get_action("same-id", "namespace-b")["delegation_id"] == "namespace-b"
