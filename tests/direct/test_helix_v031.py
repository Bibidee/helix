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
        300,
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
    warp_to(direct_vm, "2026-08-24T00:05:01Z")


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


def test_v031_transient_challenge_fetch_failure_preserves_bond_and_state(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    open_challenge(direct_vm, contract, direct_alice)
    direct_vm._helix_module.observe = lambda *args: {"kind": "observation_error", "class": "challenge_artifact_unavailable"}
    with direct_vm.expect_revert("Challenge evidence temporarily unavailable"):
        contract.review_action("action-v031")
    action = contract.get_action("action-v031")
    assert action["status"] == "challenged"
    assert action["challenge_bond_held"] == str(BOND)
    assert action["challenge_settlement"] == "held"


def test_v031_invalid_counterevidence_can_still_be_slashed(direct_vm, direct_deploy, direct_alice):
    contract = deploy(direct_vm, direct_deploy)
    create(contract)
    propose(contract)
    open_challenge(direct_vm, contract, direct_alice)
    direct_vm._helix_module.observe = lambda *args: {"kind": "observation_error", "class": "challenge_artifact_invalid"}
    contract.review_action("action-v031")
    action = contract.get_action("action-v031")
    assert action["status"] == "reviewed"
    assert action["verdict"] == "approved"
    assert action["challenge_bond_held"] == "0"
    assert action["challenge_settlement"] == "slashed"


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
    assert info["version"] == "0.3.1"
    assert info["capacity"] == {"delegations": 128, "open_actions_per_delegation": 32}
