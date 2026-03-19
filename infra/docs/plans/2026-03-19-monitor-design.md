# Infra Monitor V1 Design

Date: 2026-03-19

Status: approved for implementation

Related documents:

- [infra.md](/home/hitesh/Code/hitesh-utils/infra/infra.md)
- [external-monitors.md](/home/hitesh/Code/hitesh-utils/infra/external-monitors.md)

## 1. Goal

Build a self-hosted infrastructure monitor that runs on `vps3`, stores its data in Mongo, monitors the current infrastructure described in `infra.md`, provides an internal admin dashboard, and sends `ntfy` notifications when something goes down.

The system should be easy to extend with additional monitored targets over time without introducing a complex multi-node monitoring architecture in v1.

## 2. V1 Goals

- Run the full monitoring application on `vps3`
- Reuse existing Mongo infrastructure as the datastore
- Provide an admin dashboard accessible only over Tailscale
- Monitor the current infrastructure footprint first
- Support both dashboard-managed and config-managed monitored targets
- Use one outage level only in v1
- Send outage and recovery notifications through `ntfy`
- Keep the architecture simple: one service, central scheduling, no node agents

## 3. Non-Goals

- No public dashboard exposure in v1
- No role-based access control or multi-tenant support in v1
- No multi-node monitoring cluster or HA failover in v1
- No external monitoring service in v1
- No multiple severities, escalations, on-call rotations, or paging logic in v1
- No dashboard editing for advanced config-managed checks in v1

## 4. High-Level Architecture

The monitor is a single service deployed on `vps3`. It contains:

- a scheduler
- a check runner
- an incident/outage manager
- an `ntfy` notifier
- an internal admin dashboard
- a Mongo-backed persistence layer

The service performs direct checks from `vps3` for public or network-reachable targets and uses SSH to run deeper checks on `vps1` and `vps2`.

V1 does not use node-local agents. All orchestration happens centrally from `vps3`.

## 5. Monitoring Model

### 5.1 Target Classes

V1 supports two target classes.

`basic targets`

- created and edited in the admin dashboard
- intended for common checks
- examples: HTTP/HTTPS endpoint, TCP port, host reachability

`advanced targets`

- defined in version-controlled config
- shown in the dashboard as read-only definitions
- intended for infrastructure-aware checks
- examples: Mongo replica set health, PM2 process state, Redis checks, SSH command checks

### 5.2 Target Shape

Each monitored target should have, at minimum:

- `id`
- `name`
- `class` (`basic` or `advanced`)
- `type`
- `node` or location
- `enabled`
- `interval_seconds`
- `timeout_seconds`
- `failure_threshold`
- `recovery_threshold`
- `notify_on_failure`
- `expected_state`
- `metadata` for target-specific settings

This model must stay stable even if individual check types expand later.

### 5.3 Initial V1 Targets

Initial monitored targets should be derived from `infra.md`.

Public endpoints:

- `arlo.dog`
- `stagecouch.net`
- `hitesh.nyc`
- `hitesh.cc`

Host reachability:

- `vps1`
- `vps2`
- `vps3`

Core services:

- Caddy on `vps1`
- Caddy on `vps2`
- Redis on `vps1`
- Redis on `vps2`
- PM2-managed app runtime on `vps1`
- PM2-managed app runtime on `vps2`

Data layer:

- Mongo replica set `rs0`
- expected topology:
- `vps2` = PRIMARY
- `vps1` = SECONDARY
- `vps3` = ARBITER

## 6. Check Types

### 6.1 Basic Dashboard-Managed Checks

V1 basic checks should be limited to:

- HTTP/HTTPS status checks
- TCP port checks
- simple host reachability checks

These checks should be easy to create through the dashboard without custom code.

### 6.2 Advanced Config-Managed Checks

V1 advanced checks should support:

- SSH command checks on `vps1` and `vps2`
- Mongo replica-set health and role validation
- Redis reachability validation
- PM2 process-state validation
- custom command or script checks for future extension

Advanced checks must be implemented from an allowlisted set of check types. V1 should not allow arbitrary free-form remote execution from the dashboard.

## 7. Execution Flow

The expected execution flow is:

1. Scheduler selects due targets.
2. Check runner executes the target check.
3. Result is stored in Mongo.
4. Current status is recalculated for the target.
5. Incident logic decides whether to open, keep open, or resolve an outage.
6. If state changes, the notifier sends `ntfy` alerts.
7. Dashboard reads current status, recent runs, and outage history from Mongo.

This flow should be implemented in a way that keeps scheduling, execution, persistence, and notification concerns separate.

## 8. Outage Logic

V1 has one health state transition model only:

- `healthy`
- `down`

Recommended defaults:

- default interval: 60 seconds for most checks
- default timeout: 10 seconds for network checks
- outage opens after 3 consecutive failures
- outage resolves after 2 consecutive successes

These values should be configurable per target, but the defaults should remain simple and opinionated.

When a target is down:

- create one active outage record
- attach subsequent failed runs to the same outage
- do not open duplicate incidents for the same active problem

When a target recovers:

- mark the active outage as resolved
- record resolved timestamp
- send one recovery notification

## 9. Alerting

V1 alert transport is `ntfy`.

Notification behavior:

- send one notification when an outage opens
- send one notification when an outage resolves
- no severity levels in v1
- no escalation chains in v1
- repeated reminder notifications are optional and should default to off

The dashboard is the source of truth. Notifications are a transport layer, not the long-term system of record.

## 10. Admin Dashboard

The dashboard is Tailscale-only and should prioritize fast operational clarity over feature breadth.

V1 dashboard pages:

- `Overview`
- `Targets`
- `Outages / History`
- `Target Detail`
- `Basic Target Management`

### 10.1 Overview

Must show:

- active outages
- current status summary
- recent failures or changes
- count of healthy vs down targets

### 10.2 Targets

Must show:

- name
- target class
- type
- node or endpoint
- enabled status
- last check time
- current state
- last failure reason summary

### 10.3 Outages / History

Must show:

- currently open outages
- recent resolved outages
- opened time
- resolved time
- target name
- latest failure reason

### 10.4 Target Detail

Must show:

- target configuration
- recent check results
- current state
- outage history for that target

### 10.5 Target Management

Must support, for basic targets only:

- create
- edit
- enable
- disable

Advanced targets must be visible in the UI but read-only in v1. The UI should clearly label them as config-managed.

## 11. Data Storage

Mongo remains the datastore for v1.

The implementation should persist:

- target definitions
- check run records
- current target status
- outage records
- basic audit metadata for dashboard changes

Recommended collection boundaries:

- `targets`
- `check_runs`
- `target_status`
- `outages`
- `audit_events`

Exact schema design is up to the implementation team, but those concepts must be preserved.

## 12. Deployment And Operations

Deployment assumptions:

- one monitor app runs on `vps3`
- admin dashboard is reachable only over Tailscale
- app stores state in Mongo
- app has outbound access to `ntfy`
- app has SSH access from `vps3` to `vps1` and `vps2`

Operational expectations:

- service should restart cleanly after failure or reboot
- logs should be available locally on `vps3`
- secrets must be injected at runtime, not committed
- SSH should use a dedicated key with least privilege where practical

The exact process manager or packaging model is an implementation detail. The design only requires a single deployable unit with clear restart and logging behavior.

## 13. Security Assumptions

- Dashboard is not public
- Access is limited by Tailscale network reachability
- Secrets are stored outside repo config
- Advanced checks are allowlisted and controlled in code/config
- V1 assumes a small trusted operator set and does not require complex authorization controls

## 14. Extensibility Requirements

The system must stay easy to extend in these ways:

- add new basic targets through the dashboard
- add new advanced targets through config
- add new advanced check types without redesigning the dashboard data model
- later add one external monitor to watch `vps3` and critical public endpoints

V1 should not make future external monitoring harder. A later external monitor should be able to watch either public URLs or heartbeat-style endpoints exposed by the monitor service.

## 15. Acceptance Criteria

Implementation is complete for v1 when all of the following are true:

- A monitor service runs on `vps3` as a single deployable unit.
- The service uses Mongo for persistence.
- The admin dashboard is accessible only inside Tailscale.
- Basic targets can be created, edited, enabled, and disabled through the dashboard.
- Advanced targets can be loaded from config and displayed as read-only in the dashboard.
- The initial infrastructure targets from `infra.md` can be represented in the system.
- `vps3` can execute direct checks and SSH-based deep checks on `vps1` and `vps2`.
- The system tracks current target status and retains recent check history.
- The system opens one outage after consecutive failures and resolves it automatically after recovery.
- Opening an outage sends one `ntfy` notification.
- Resolving an outage sends one `ntfy` recovery notification.
- The dashboard clearly shows active outages, recent history, target status, and target details.

## 16. Deferred Work

The following items are intentionally deferred:

- external monitoring for `vps3`
- SMS alerts
- multi-severity incidents
- alert escalation policies
- node-local agents
- public access to the dashboard
- edit support in the dashboard for advanced targets

## 17. Recommended Next Step

Create an implementation plan that breaks this design into:

- data model and persistence work
- scheduler and check-runner work
- SSH-based advanced check implementation
- outage and notification logic
- dashboard and CRUD flows for basic targets
- deployment setup on `vps3`
