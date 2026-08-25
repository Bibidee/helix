# Deployment evidence

## Helix v0.5.1 — RELEASE RECORD

The v0.5.0 deployment below is historical. This record is populated only after a fresh v0.5.1 deployment, finalized source parity, and fresh live evidence are complete.

- Source commit: pending
- Contract: pending
- Deployment transaction: pending
- Finalized status / GenVM execution: pending
- Source bytes / SHA-256 / Git blob: pending
- Finalized source parity: pending
- Live v0.5.1 evidence: pending

## Helix v0.5.0 — HISTORICAL SOURCE-MATCHED DEPLOYMENT

The v0.5.0 deployment is [`0xDEB91F9682C4F89980CdCD059c89A2148d11D819`](https://explorer-studio.genlayer.com/address/0xDEB91F9682C4F89980CdCD059c89A2148d11D819), deployment transaction [`0x01966b9980881cec81a2b95455c99c5a6c093dfb0ff6c1278eafe23eec1f09d1`](https://explorer-studio.genlayer.com/tx/0x01966b9980881cec81a2b95455c99c5a6c093dfb0ff6c1278eafe23eec1f09d1), source commit `e6a13d9`, 31,365 bytes, SHA-256 `695cfc1ed2c969159e00d4bd775d2a41aac84edca6033ca8307ba381149346b6`, exact retrieved-source parity `YES`. It is historical because v0.5.1 moves counterevidence admission into a nondeterministic consensus block.

## Helix v0.4.0 — HISTORICAL SOURCE-MATCHED DEPLOYMENT

The v0.4.0 source is deployed at [`0xfB191c351c51B20d0A84F2B1363b0e151300704E`](https://explorer-studio.genlayer.com/address/0xfB191c351c51B20d0A84F2B1363b0e151300704E), deployment transaction [`0x82627948ec2271a8a5e00e4fd5e20173d89bf5d2ac0bc8127a935ee8c69808aa`](https://explorer-studio.genlayer.com/tx/0x82627948ec2271a8a5e00e4fd5e20173d89bf5d2ac0bc8127a935ee8c69808aa), source commit `5545800ee64223dc5aaac4715d7ce8e8f56cc0a4`, 31,652 bytes, SHA-256 `a4caf0763bd72db399c29962074a5fcc5875dece6631a6286248454fba9c338a`, exact retrieved-source parity `YES`. Deployment finalized with `MAJORITY_AGREE` and GenVM `SUCCESS`. It is historical after v0.5.0 source changes.

Live v0.4.0 receipts: delegation `0x02e72d9e90be1b316a1a0c5ef7b090cc530dd8712fc4f63664591df17cfadb61`; safe proposal `0x1da7087cbf4d19d7eeaea8f5aaf43c8c70eb0fc3b9cb025bb6fd576a701c320d`; safe review `0x3a72f4fb018008c0c6207992dd4a93d9deabd1e9db800b014eb0fefd9c9ca7e7` finalized `reviewed / approved`; unsafe proposal `0xb1c1952d8ee6aa9da9689c948a64b35edef20598052b11a361f9963c1af33800`; unsafe review `0xf4cb2cf0a30fc971bbf19b5081aa2f93c6472c857ba4c9f5b71daba0261d423d` finalized `reviewed / blocked`; replay `0xae91e2000ab9153c9a59b313b2030fce9d999ef9055fbae34b68e34b23fd025a` finalized with `[EXPECTED] Action commitment already registered`; inconclusive proposal `0xf16e30ba4aebcf88efea4e5adb5fe85501e3bbdcaef86b329de7fec535de84be` and review `0xfcba757925a9b9e22ecf5904bd1a481fe0ef52267dfbb354d8daea251c89f38d` finalized `reviewed / inconclusive`, confidence 10; valid bonded challenge `0xcc7878e06b750c9a288a571b79673603589e7b5474623201ad5f3249504ded3b` finalized from challenger `0xae82EFfe54dCcfd170d9a08EeE128339A70347f7` with exact `0.001 GEN` held and state `challenged`.

### Historical v0.4.0 tradeoff note

The v0.4.0 release used a bounded lifetime challenge round. Its timeout/availability behavior is historical and was replaced by v0.5.0’s snapshot-and-refund rules; it must not be used to describe the current source.

The v0.4.0 safe consumption, double-consume rejection, challenged re-review, and final bond settlement receipts were protocol-time-gated and are not promoted as v0.5.0 evidence.

The post-deployment validator-divergence regression suite uses `direct_vm.run_validator()` with changed validator-side mocks and passes without modifying `contracts/helix.py`. The frozen source remains 31,652 bytes with SHA-256 `a4caf0763bd72db399c29962074a5fcc5875dece6631a6286248454fba9c338a`.

## Helix v0.3.1 — HISTORICAL SOURCE-MATCHED DEPLOYMENT

The current repository source contains material security fixes beyond the historical v0.3.0 deployment. The final v0.3.1 deployment is [`0xD94f2e7c0CF068F0FF3C2bD8a95c8Cdf85A14fd2`](https://explorer-studio.genlayer.com/address/0xD94f2e7c0CF068F0FF3C2bD8a95c8Cdf85A14fd2), deployment transaction [`0x265c3a83f74b879ce054cee68e6740b1ed7173d34ed96b09a301738281318683`](https://explorer-studio.genlayer.com/tx/0x265c3a83f74b879ce054cee68e6740b1ed7173d34ed96b09a301738281318683), source commit `c36c62ca2392c8ff0564ee2958f4a4c4e2fc2f3c`, local/retrieved size 29,950 bytes, SHA-256 `aad454d0b315879940802dfdf3659ebe74b2c1eb18eae246cebf296f2f462684`, exact parity `YES`. Deployment consensus was `MAJORITY_AGREE` with leader GenVM `SUCCESS`.

v0.3.1 changes include:

- transient challenge-artifact retrieval failures remain retryable and preserve challenged state/bond;
- deterministically invalid supplied counterevidence remains slashable;
- consumer cannot equal the challenge sink and is treated as an interested party for challenge initiation;
- challenged closure/expiry cancellation releases per-delegation open-action capacity;
- `get_info()` reports the actual enforced capacity model;
- finalized source retrieval uses the current `gen_getContractCode` request shape.

Final-deployment live delegation/proposal/review transactions submitted so far: delegation `0x550d4ec9149638df67cbd156c469e91225f75cb6d51ae7e8278954ec363fca69`, safe proposal `0xe65ca3cb2af2016776d439fbc3799c99c01d2ae2a64a354d27a407b00fca2a17`, safe review `0xd60a5b8d9588aac16f634f521abb05182fda921d4d1c8d3755197dbd3beb9fe0`. Studionet state reads for the review are currently unavailable; no safe verdict or later live path is claimed until finalized state is observable.

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
