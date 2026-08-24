import fs from "node:fs/promises";
import path from "node:path";
import { Wallet } from "ethers";

const password = process.env.HELIX_WALLET_PASSWORD;
const output = process.env.HELIX_KEYSTORE;
if (!password || !output) throw new Error("HELIX_WALLET_PASSWORD and HELIX_KEYSTORE are required");
await fs.mkdir(path.dirname(output), { recursive: true });
try {
  await fs.access(output);
  throw new Error("Refusing to overwrite an existing keystore");
} catch (error) {
  if (error.code !== "ENOENT") throw error;
}
const wallet = Wallet.createRandom();
await fs.writeFile(output, await wallet.encrypt(password), { encoding: "utf8", mode: 0o600 });
console.log(JSON.stringify({ created: output, address: wallet.address }, null, 2));
