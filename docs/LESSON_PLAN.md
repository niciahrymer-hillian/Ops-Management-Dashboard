# 📖 Lesson Plan — Ops-Management-Dashboard

> **Chain C — Full-Stack + Infrastructure** | Real-time ops dashboard — WebSockets, RBAC, live UI updates.

## What This Project Is

Build an internal operations dashboard: aggregate service health and business metrics into one view people actually check.

## Learning Objectives

By the end I can:

1. Choose metrics that drive a decision rather than fill space.
2. Aggregate data from several services into one view.
3. Separate system health from business health.
4. Design alerting that signals rather than spams.
5. Handle a data source being unavailable without blanking the page.
6. Build for the person who checks it every morning.

## Software You Will Use

- A frontend framework (React) or Grafana.
- A backend API for aggregation.
- PostgreSQL and/or Prometheus.

## Build Order

1. Interview the intended user about what they actually need to know.
2. Define each metric precisely, including edge cases.
3. Build the aggregation layer with caching.
4. Build the dashboard view.
5. Handle partial failure so one dead source does not blank the page.
6. Add alerting with deliberately chosen thresholds.

## Common Mistakes to Avoid

- Displaying every available metric instead of the decision-relevant ones.
- Ambiguous metric definitions that two people read differently.
- A failed data source rendering as zero instead of as an error.
- Alert thresholds set by guesswork.
- Building it without asking the person who will use it.

## Check Your Understanding

The quiz covers metric selection, partial-failure handling, and alert threshold design.

## Why This Matters (Industry Application)

Internal tooling is a large share of real engineering work and is chronically undervalued. A dashboard that surfaces the right signal — and stays quiet otherwise — saves an operations team hours daily. Knowing which metrics matter is the hard part, and it comes from understanding the operation, not the code.

## Reflection Questions

- Which number on this dashboard would actually change someone's behaviour today?
- How would a user tell the difference between 'zero' and 'we could not load this'?
