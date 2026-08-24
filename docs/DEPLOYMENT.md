# Deployment evidence

## Helix v0.3.1 — RELEASE CANDIDATE, NOT YET DEPLOYED

The current repository source contains material security fixes beyond the source-matched v0.3.0 deployment. Do not present the v0.3.0 address as v0.3.1 evidence.

v0.3.1 changes include:

- transient challenge-artifact retrieval failures remain retryable and preserve challenged state/bond;
- deterministically invalid supplied counterevidence remains slashable;
- consumer cannot equal the challenge sink and is treated as an interested party for challenge initiation;
- challenged closure/expiry cancellation releases per-delegation open-action capacity;
- `get_info()` reports the actual enforced capacity model;
- finalized source retrieval uses the current `gen_getContractCode` request shape.

Required final release evidence: Python 3.12 preflight, finalized deployment/GenVM success, full source commit SHA, local and retrieved SHA-256 parity, finalized safe `APPROVED`, finalized clearly unsafe `BLOCKED`, and finalized challenge/settlement proof. No v0.3.1 on-chain outcome is claimed here yet.

## Helix v0.3.0 — HISTORICAL SOURCE-MATCHED DEPLOYMENT

The frozen v0.3.0 source is deployed at [`0x0bC80b70F87b493F12aBd27461666052a9FF8B57`](https://explorer-studio.genlayer.com/address/0x0bC80b70F87b493F12aBd27461666052a9FF8B57) by [`0xb01c466981a6ff19d6fb494f9d73181d167c7ff02e1fd1dafc25e41a43148f2b`](https://explorer-studio.genlayer.com/tx/0xb01c466981a6ff19d6fb494f9d73181d167c7ff02e1fd1dafc25e41a43148f2b). Repository-recorded deployment consensus was `MAJORITY_AGREE` with leader GenVM `SUCCESS`. Source commit: `7fadc5391718379777532cf4f4414a183f7b7594`. Local and retrieved source were both 28,684 bytes with SHA-256 `db673f3d7e905127505d2f5dde47fab8cb6381482f50932f78e61fcca7e1b65b`; parity was byte-for-byte `YES`.

This deployment remains historical after v0.3.1 source changes. Old `UNDETERMINED` transactions, if visible in explorer history, are not treated as finalized evidence.

## Helix v0.2.0 — HISTORICAL DEPLOYMENT

Contract: [`0x102D10244eF839119950b752aD67Fbf001123ef7`](https://explorer-studio.genlayer.com/address/0x102D10244eF839119950b752aD67Fbf001123ef7)

Deployment transaction: [`0x0225fd85059c8d5d4153d056dce41cd7116c388248cd78a0e6692632187752ba`](https://explorer-studio.genlayer.com/tx/0x0225fd85059c8d5d4153d056dce41cd7116c388248cd78a0e6692632187752ba)

Historical v0.2.0 live evidence recorded in earlier release work includes a finalized safe review (`0x4d4e52bcc85ef504ec9daba02dcc153ac3d49f70a341a8177ab75e72c4a16bdc`) with on-chain `reviewed / approved` state at confidence 87. An unsafe proposal was submitted, but no finalized blocked outcome is promoted as release evidence here.

## Helix v0.1.3 — HISTORICAL SOURCE-MATCHED DEPLOYMENT

- Contract: [`0x92eD41aFC028a67857BDAF7625378E3aF431d620`](https://explorer-studio.genlayer.com/address/0x92eD41aFC028a67857BDAF7625378E3aF431d620)
- Deployment transaction: [`0x1b7398502fd0fee14adffc28c04af09e6b12553cf1c5f9c54103af34227082c2`](https://explorer-studio.genlayer.com/tx/0x1b7398502fd0fee14adffc28c04af09e6b12553cf1c5f9c54103af34227082c2)
- Source commit: `198fdba01939bc9b0044e1e8725e0fb64077274d`
- Result: `FINALIZED`, majority agreement, GenVM `SUCCESS`.
- Local/deployed SHA-256: `087f3220fa919a5936f046500a6a4a94c4d2dc726f008ac650d5481c4369c60a`
- Parity: exact byte-for-byte match.

Verified historical safe path:

- Delegation creation: `0xb81f5b0200a1aae055f0d2f26b90f59d2f661d2281fc352a7a38e58a9a1a8448`
- Safe proposal: `0x9c4d73f0a3c6d59d5c3683b0a1837300edac2e60d214ef821161621d77ec6270`
- Safe review: `0x61294e91ad7651d9995bd2d951ff2792bbe0e071224ecf28c065cf9801363911` — finalized `APPROVED`, confidence 91
- Consumption: `0x546c3f101609d119fa694d556f206785fe681ff3d177910efcb2a97b813a653c` — finalized, final action status `consumed`

A previously submitted unsafe-review transaction (`0xbe60e3006b710cb2fa05569723cf839bc1f1db5e30b914a91f275376c5222620`) is intentionally not presented as a blocked-path result because no finalized verdict is claimed for it.

## Helix v0.1.0 — LEGACY

- Contract: [`0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732`](https://explorer-studio.genlayer.com/address/0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732)
- Deployment transaction: [`0x92b9cab4228f684f5d7406869b5447f801f59dca49da8aa3f4bbf271f8cb4b0a`](https://explorer-studio.genlayer.com/tx/0x92b9cab4228f684f5d7406869b5447f801f59dca49da8aa3f4bbf271f8cb4b0a)
- Result: `FINALIZED`, majority agreement, GenVM `SUCCESS`.
- Local/deployed SHA-256: `40a561e42421ec6e4f13d63748c4b5c64849893f86a1bab023f35a6c1e4a0c89`
- Parity: exact byte-for-byte match.

v0.1.1 and v0.1.2 were superseded release candidates. v0.1.4 did not replace the current v0.3.x line and is historical development context only.
