import fs from "node:fs/promises";
import crypto from "node:crypto";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";

const address = process.argv[2];
if (!address) throw new Error("Usage: node scripts/verify_source_parity.mjs <contract-address>");
const client = createClient({ chain: studionet, endpoint: process.env.HELIX_RPC || "https://studio.genlayer.com/api" });
const local = await fs.readFile("contracts/helix.py");
const encoded = await client.request({ method: "gen_getContractCode", params: [{ address, status: "finalized" }] });
const text = String(encoded);
const retrieved = Buffer.from(text.startsWith("0x") ? text.slice(2) : text, text.startsWith("0x") ? "hex" : "base64");
const hash = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");
console.log(JSON.stringify({ address, localBytes: local.length, retrievedBytes: retrieved.length, localSha256: hash(local), retrievedSha256: hash(retrieved), parity: local.equals(retrieved) }, null, 2));
