# Council seat lifecycle (v2.6 RC)

This document describes seat lifecycle events for council governance operations.

## States

1. `assigned` — seat mapped to an occupant and weight.
2. `challenged` — a challenge has been opened for the seat.
3. `deactivated` — challenge upheld and seat is inactive.
4. `reassigned` — seat assigned to a new occupant.

## Data source

`council_seat_lifecycle` stores event-sourced transitions from governance events.

## Operator checks

- Every `challenged` event should eventually become `deactivated` or `reassigned`.
- Active seat count should match governance contract snapshots for the current term.
