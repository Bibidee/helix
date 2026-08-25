import fs from "node:fs/promises";
import crypto from "node:crypto";

const address = process.argv[2];
if (!address) throw new Error("Usage: node scripts/verify_source_parity.mjs <contract-address>");
const local = await fs.readFile("contracts/helix.py");
const endpoint = process.env.HELIX_RPC || "https://studio.genlayer.com/api";
const rpc = await fetch(endpoint, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "gen_getContractCode", params: [{ address, status: "finalized" }] }) });
if (!rpc.ok) throw new Error(`Finalized source RPC failed: HTTP ${rpc.status}`);
const payload = await rpc.json();
if (payload.error) throw new Error(`Finalized source RPC failed: ${JSON.stringify(payload.error)}`);
if (typeof payload.result !== "string" || !payload.result) throw new Error("No finalized contract code returned");
const retrieved = Buffer.from(payload.result, "base64");
if (!retrieved.length) throw new Error("Decoded finalized contract code is empty");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const result = { address, state: "FINALIZED", localBytes: local.length, retrievedBytes: retrieved.length, localSha256: hash(local), retrievedSha256: hash(retrieved), parity: local.equals(retrieved) };
console.log(JSON.stringify(result, null, 2));
if (!result.parity || result.localBytes !== result.retrievedBytes) process.exitCode = 1;
