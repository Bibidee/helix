import fs from "node:fs/promises";
import { setTimeout as delay } from "node:timers/promises";
import { Wallet } from "ethers";
import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { privateKeyToAccount } from "viem/accounts";

const keystore = process.env.HELIX_KEYSTORE;
const password = process.env.HELIX_WALLET_PASSWORD;
if (!keystore || !password) throw new Error("HELIX_KEYSTORE and HELIX_WALLET_PASSWORD are required");
const wallet = await Wallet.fromEncryptedJson(await fs.readFile(keystore, "utf8"), password);
const client = createClient({ chain: studionet, endpoint: process.env.HELIX_RPC || "https://studio.genlayer.com/api", account: privateKeyToAccount(wallet.privateKey) });
const code = await fs.readFile("contracts/helix.py", "utf8");
const hash = await client.deployContract({ code, args: [wallet.address], consensusMaxRotations: 5 });
console.log(JSON.stringify({ deploymentTransaction: hash, owner: wallet.address }, null, 2));
for (let attempt = 0; attempt < 180; attempt++) {
  await delay(5000);
  const transaction = await client.getTransaction({ hash });
  if (!["FINALIZED", "UNDETERMINED", "CANCELED"].includes(transaction.statusName)) continue;
  const validators = transaction.consensus_data?.validators || [];
  const validator = validators.find((item) => item.mode === "leader") || validators[0];
  const address = transaction.data?.calldata?.contractAddress || transaction.recipient || transaction.to;
  const result = { deploymentTransaction: hash, status: transaction.statusName, result: transaction.result_name, execution: validator?.execution_result, rotations: transaction.rotation_count, contractAddress: address, explorer: address ? `https://explorer-studio.genlayer.com/address/${address}` : undefined };
  console.log(JSON.stringify(result, null, 2));
  if (result.status !== "FINALIZED" || result.execution !== "SUCCESS" || !address) process.exitCode = 1;
  process.exit();
}
throw new Error(`Deployment timeout: ${hash}`);
