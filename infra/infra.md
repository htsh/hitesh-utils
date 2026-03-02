# Infrastructure Inventory (Reusable Deploy Targets)

Last updated: 2026-03-02 (source reference was 2026-02-24; added bandwidth notes + `stagecouch.net`)

## Summary

Three VPS nodes connected via **Tailscale** (`vps1`, `vps2`, `vps3`). Typical pattern:

* `vps1`: public edge + app hosting (best place for internet-facing services)
* `vps2`: data/ingest/heavy workloads (best place for databases, workers, high I/O)
* `vps3`: light utility + quorum roles (keep low-noise / stable)

---

## Node Inventory

| Node   | OS        | CPU     | RAM    | Disk              | Bandwidth           | Primary Role                 |
| ------ | --------- | ------- | ------ | ----------------- | ------------------- | ---------------------------- |
| `vps1` | AlmaLinux | 2 cores | 4 GB   | 70 GB NVMe        | **Unmetered**       | Public edge + app node       |
| `vps2` | Ubuntu    | 6 cores | 8 GB   | 120 GB RAID10 SSD | **Metered (~9 TB)** | Data + ingest heavy node     |
| `vps3` | Ubuntu    | 2 cores | 2.5 GB | 40 GB RAID10 SSD  | **Metered (~7 TB)** | Arbiter / light utility node |

---

## Domains / DNS Mapping

* `arlo.dog` → `vps1`
* `stagecouch.net` → `vps1`
* `hitesh.nyc` → `vps2`
* `hitesh.cc` → `vps3`

---

## Networking

* Inter-node communication over **Tailscale**

  * Node hostnames on tailnet: `vps1`, `vps2`, `vps3`
* Internal services should bind to:

  * `localhost` and/or the **Tailscale interface**
* Prefer exposing public services via the edge node (`vps1`) rather than opening ports on all nodes.

---

## Shared Platform Services (Current Footprint)

### Reverse Proxy / TLS

* **Caddy**

  * Installed on `vps1` and `vps2`
  * Typical configuration: `vps1` serves as the active public edge; `vps2` can act as standby or internal edge if needed.

### Data Store

* **MongoDB** across all three nodes in a replica set topology:

  * Replica set: `rs0`
  * `vps2:27017` = **PRIMARY**
  * `vps1:27017` = **SECONDARY**
  * `vps3:27017` = **ARBITER** (non data-bearing)

### Cache / Queueing (Lightweight)

* **Redis**

  * Installed on `vps1` and `vps2`
  * Typical pattern: `vps2` hosts the “shared” Redis used by applications; `vps1` may have local Redis for node-local needs.

### Process Management (App Nodes)

* **PM2** is used as a process manager for Node-based services on app-capable nodes (`vps1`, `vps2`) where applicable.

---

## Default Placement Guide (Deploy Heuristics)

Use these defaults when choosing a deploy target:

* Put **public web frontends** and **reverse-proxy entrypoints** on `vps1`.

  * Best for websites, dashboards, and anything that needs stable public ingress.
* Put **data-heavy**, **ingestion-heavy**, or **background-processing** workloads on `vps2`.

  * Best for databases, workers, queues, analytics, and high-query APIs.
* Keep `vps3` **quiet and stable**.

  * Good for quorum/arbiter roles and tiny utility services.
  * Avoid heavy containers, memory spikes, or noisy workloads.

---

## Practical Examples (Generic)

* Blog / CMS:

  * Web frontend on `vps1`
  * Database on `vps2` (if self-hosted)
* Public-facing microservice:

  * Public ingress on `vps1` (Caddy)
  * Service runtime on `vps1` or `vps2` depending on CPU/data needs
* Worker / ingest pipeline:

  * Run on `vps2`
  * Keep any required state (DB/Redis) on `vps2` unless replication is required

---

## Operational Notes (Keep Updated)

* Track which node is the **active edge** for each public domain (usually `vps1`).
* Re-check Redis usage: shared on `vps2` vs node-local on `vps1`.
* Keep Mongo replica set membership/roles consistent (`vps2` primary, `vps1` secondary, `vps3` arbiter).
* Ensure projects document:

  * which domains they use
  * which nodes host app vs data vs workers
  * which internal ports/services are reachable over Tailscale vs public ingress

