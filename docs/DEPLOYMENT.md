# Deployment evidence

## Helix v0.1.3 — CURRENT

- Contract: [`0x92eD41aFC028a67857BDAF7625378E3aF431d620`](https://explorer-studio.genlayer.com/address/0x92eD41aFC028a67857BDAF7625378E3aF431d620)
- Deployment transaction: [`0x1b7398502fd0fee14adffc28c04af09e6b12553cf1c5f9c54103af34227082c2`](https://explorer-studio.genlayer.com/tx/0x1b7398502fd0fee14adffc28c04af09e6b12553cf1c5f9c54103af34227082c2)
- Source commit: `198fdba01939bc9b0044e1e8725e0fb64077274d`
- Result: `FINALIZED`, majority agreement, GenVM `SUCCESS`.
- Local/deployed SHA-256: `087f3220fa919a5936f046500a6a4a94c4d2dc726f008ac650d5481c4369c60a`
- Parity: retrieved source is an exact byte-for-byte match.

### Verified live evidence

Safe path:

- [Delegation creation](https://explorer-studio.genlayer.com/tx/0xb81f5b0200a1aae055f0d2f26b90f59d2f661d2281fc352a7a38e58a9a1a8448): `FINALIZED`, GenVM `SUCCESS`.
- [Safe proposal](https://explorer-studio.genlayer.com/tx/0x9c4d73f0a3c6d59d5c3683b0a1837300edac2e60d214ef821161621d77ec6270): `FINALIZED`, GenVM `SUCCESS`.
- [Safe review](https://explorer-studio.genlayer.com/tx/0x61294e91ad7651d9995bd2d951ff2792bbe0e071224ecf28c065cf9801363911): finalized `APPROVED`, confidence 91.
- [Consumption](https://explorer-studio.genlayer.com/tx/0x546c3f101609d119fa694d556f206785fe681ff3d177910efcb2a97b813a653c): `FINALIZED`, GenVM `SUCCESS`; final action status is `consumed`.

Only finalized outcomes are counted as verified live evidence. A previously submitted unsafe-review transaction (`0xbe60e3006b710cb2fa05569723cf839bc1f1db5e30b914a91f275376c5222620`) is intentionally not presented as a blocked-path result here because no finalized verdict is being claimed for it in this release record.

Challenge, refund, blocked, inconclusive, closure, expiry, and replay protections are covered by the Direct Mode adversarial suite. Live challenge/refund evidence may be added later only after the corresponding Studionet transactions finalize; its absence does not alter the source-matched deployment record above.

## Helix v0.1.0 — LEGACY

- Contract: [`0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732`](https://explorer-studio.genlayer.com/address/0x21acd955Fe3E87EC642C6d3a0aE8a46787AD0732)
- Deployment transaction: [`0x92b9cab4228f684f5d7406869b5447f801f59dca49da8aa3f4bbf271f8cb4b0a`](https://explorer-studio.genlayer.com/tx/0x92b9cab4228f684f5d7406869b5447f801f59dca49da8aa3f4bbf271f8cb4b0a)
- Result: `FINALIZED`, majority agreement, GenVM `SUCCESS`, empty stdout/stderr.
- Local/deployed SHA-256: `40a561e42421ec6e4f13d63748c4b5c64849893f86a1bab023f35a6c1e4a0c89`
- Parity: retrieved source is an exact byte-for-byte match (23,331 characters).

v0.1.1 and v0.1.2 were superseded release candidates and are not presented as current deployments. The v0.1.3 deployment above is current; it makes a successful single challenged re-review final immediately while preserving deterministic closure/expiry refunds.
