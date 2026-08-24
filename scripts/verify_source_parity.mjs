import fs from "node:fs/promises";
import crypto from "node:crypto";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = process.argv[2];
if (!address) throw new Error("Usage: node scripts/verify_source_parity.mjs <contract-address>");
const client = createClient({ chain: studionet, endpoint: process.env.HELIX_RPC || "https://studio.genlayer.com/api" });
const local = await fs.readFile("contracts/helix.py");
const source = await client.getContractCode(address);
if (!source) throw new Error("No finalized contract code returned");
const retrieved = Buffer.from(source, "utf8");
if (!retrieved.length) throw new Error("Decoded finalized contract code is empty");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
const result = { address, localBytes: local.length, retrievedBytes: retrieved.length, localSha256: hash(local), retrievedSha256: hash(retrieved), parity: local.equals(retrieved) };
console.log(JSON.stringify(result, null, 2));
if (!result.parity || result.localBytes !== result.retrievedBytes) process.exitCode = 1;
