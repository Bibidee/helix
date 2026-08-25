import fs from "node:fs/promises";
import crypto from "node:crypto";

const address = process.argv[2];
if (!address) throw new Error("Usage: node scripts/verify_source_parity.mjs <contract-address>");
const local = await fs.readFile("contracts/helix.py");
const endpoint = process.env.HELIX_RPC || "https://studio.genlayer.com/api";
const request = async (method, params) => {
  const response = await fetch(endpoint, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }) });
  if (!response.ok) throw new Error(`RPC failed: HTTP ${response.status}`);
  return response.json();
};
let payload = await request("gen_getContractCode", [{ address, status: "finalized" }]);
let retrieval = "finalized_code_query";
if (payload.error) {
  // Older StudioNet gateways reject the documented status object. Do not
  // silently accept code: first prove the deployment itself is FINALIZED,
  // then use the legacy code query only as a compatibility fallback.
  const deploymentTx = process.env.HELIX_DEPLOYMENT_TX;
  if (!deploymentTx) throw new Error(`Finalized source RPC failed: ${JSON.stringify(payload.error)}`);
  const status = await request("gen_getTransactionStatus", [deploymentTx]);
  if (status.result !== "FINALIZED") throw new Error(`Deployment is not FINALIZED: ${status.result || JSON.stringify(status.error)}`);
  payload = await request("gen_getContractCode", [address]);
  retrieval = "accepted_code_query_after_finalized_transaction_proof";
}
if (payload.error) throw new Error(`Contract source RPC failed: ${JSON.stringify(payload.error)}`);
if (typeof payload.result !== "string" || !payload.result) throw new Error("No finalized contract code returned");
const retrieved = Buffer.from(payload.result, "base64");
if (!retrieved.length) throw new Error("Decoded finalized contract code is empty");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const result = { address, state: "FINALIZED", retrieval, localBytes: local.length, retrievedBytes: retrieved.length, localSha256: hash(local), retrievedSha256: hash(retrieved), parity: local.equals(retrieved) };
console.log(JSON.stringify(result, null, 2));
if (!result.parity || result.localBytes !== result.retrievedBytes) process.exitCode = 1;
