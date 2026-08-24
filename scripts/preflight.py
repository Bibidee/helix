"""Portable release gate for the single deployable Helix source."""
import ast
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = list((ROOT / "contracts").glob("*.py"))
if len(CONTRACTS) != 1 or CONTRACTS[0].name != "helix.py":
    raise SystemExit("Expected exactly one deployable source: contracts/helix.py")
source = CONTRACTS[0].read_text(encoding="utf-8")
ast.parse(source)
required = [
    "class Helix", "run_nondet_unsafe", "def fetch_verified", "hashlib.sha256",
    "challenge_bond_held", "challenge_round_completed", "finalized = action.challenge_round_completed",
    "settle_expired_challenge", "def is_actionable", "def canonical_hash(value)",
    '"version": "0.3.1"', "return verdict(left) == verdict(right)", "occurrence_nonce",
    "commitments", "MAX_OPEN_ACTIONS_PER_DELEGATION", "open_action_count", "capacity_released",
    "consumer: Address", "Consumer only", "Consumer cannot be challenge sink", "delegation.consumer",
    "challenge_artifact_unavailable", "challenge_artifact_invalid", "http_unavailable",
    "release_capacity(action, delegation); ChallengeSettled", "open_actions_per_delegation",
    "MIN_WINDOW", "300, 30 * 24 * 60 * 60", "self.actions.get(action_id) is not None",
]
missing = [item for item in required if item not in source]
if missing: raise SystemExit(f"Missing Helix safety invariants: {missing}")
artifacts = ROOT / "artifacts"; artifacts.mkdir(exist_ok=True)
linter = shutil.which("genvm-lint") or shutil.which("genvm-lint.exe")
if linter is None:
    executable = "genvm-lint.exe" if sys.platform == "win32" else "genvm-lint"
    for candidate in (Path(sys.executable).parent / executable, Path(sys.executable).parent / "Scripts" / executable):
        if candidate.exists(): linter = str(candidate); break
if linter is None: raise SystemExit("genvm-lint executable not found; install pinned requirements")
for command in (
    [sys.executable, "-m", "pytest", "tests/direct", "-q"],
    [linter, "check", str(CONTRACTS[0]), "--json"],
    [linter, "schema", str(CONTRACTS[0]), "--output", str(artifacts / "helix.abi.json")],
):
    result = subprocess.run(command, cwd=ROOT)
    if result.returncode != 0: raise SystemExit(result.returncode)
print(f"Helix preflight passed: {len(required)} invariants, Direct Mode, lint, and schema")
