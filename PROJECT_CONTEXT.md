# YouTube Shorts Automated — Project Context & Governing Rules

This file is the source of truth for the rebuild of **YouTube-Shorts-Automated**.

Before making **any edit** to this repository, ChatGPT must read this file in full and follow every rule below. After every improvement or functional change, this file must be updated to reflect the current architecture, completed work, constraints, and any newly established rules.

## 1. Two-pipeline development model

The factory has exactly two pipelines:

- **Test pipeline** — new functions are built and validated here first.
- **Live pipeline** — production workflow that is assembled only from functions that have already been tested and approved.

This sequence is mandatory for **every edit**:

1. Build or change the function in the **test pipeline**.
2. Test and validate that function independently.
3. Only after it works correctly, integrate/stitch it into the **live pipeline**.
4. Validate the live handover/integration.

Do not bypass the test stage by directly changing the live pipeline.

## 2. No wrappers

**Never add wrappers around existing code or functions.**

When an existing function needs to change, delete the old implementation and rewrite the function cleanly where appropriate. Do not preserve bad architecture merely to avoid rewriting it.

No compatibility wrappers, adapter wrappers, proxy functions, fallback wrappers, or scaffolding whose purpose is only to avoid a clean rewrite.

## 3. Final-Shorts is a baseline, not a code source

**Do not copy code from the `AakarshBot/Final-Shorts` repository.**

Final-Shorts exists only as the conceptual/functional baseline for understanding what the factory currently does and what capabilities may need to be rebuilt.

All implementation in this repository must be **coded from scratch**.

That means:

- No copied functions.
- No copied modules.
- No copied implementation blocks.
- No copy-paste of old architecture.
- No importing code from Final-Shorts at runtime.
- No treating Final-Shorts as a dependency.

We may independently recreate equivalent functionality when required, but the implementation must be newly written for this repository.

## Operating rule

Every future change must respect all three rules above.

The repository context must be read **before every edit** and updated **after every improvement**.
