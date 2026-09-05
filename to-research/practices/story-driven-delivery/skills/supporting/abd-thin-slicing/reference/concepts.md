# Thin Slicing — Core Concepts

**Gap discipline.** Do not invent stories or increments to fill holes — see [`../../../reference/handling-incomplete-context.md`](../../../reference/handling-incomplete-context.md).

## What is a Story Map Increment?

An increment is a **named, ordered slice** of the story map you plan to **ship or learn from before** the next slice. It groups **existing stories** (verb–noun, flow order) under one increment: a **sequenced backlog grouping**, not a new epic. This skill turns a story map into a map **with increments**.

## What is thin slicing?

**Thin slicing** means choosing the **smallest** increment that still **completes a meaningful journey** (value, demo, or learning)—often by taking **just enough** from multiple areas to achieve end-to-end flow, rather than finishing one part in depth. Early increments often **trade polish for speed** (e.g., manual steps, stubs, just one data path) to ensure we get **quick, concrete feedback**.

This approach is especially useful in AI-heavy work, where it's easy to go down the wrong path. Thin slices act as "early checkpoints" — before an AI creates large output based on one or two erroneous assumptions. Running an initial thin slice can quickly expose mismatches, missing context, or learning gaps.

Later slices then **add quality, automation, or robustness** — refining the same journey with better tech or user experience (for example, moving from "Manual…" to "Automated…"). The goal: visible, valuable progress **with every slice**.

## Vertical vs horizontal slices

- **Vertical (preferred):** The increment cuts **across** epics/features: a little of order entry, payment, storage, confirmation — enough to go **end-to-end** (input → processing → persistence/feedback → visible outcome) in one slice.
- **Horizontal (avoid):** Finish **all** of Epic A, then **all** of Epic B — layers that **cannot** be exercised end-to-end until late increments.
