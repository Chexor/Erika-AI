# Erika Reconstruction Protocol

**Status:** ACTIVE
**Mandate:** Zero-tolerance for architectural purity. Stability, modularity, and test-driven excellence over speed.

## 1. THE ARCHITECTURAL LAW
Erika is a Four-Layer Modular System. You must strictly adhere to these boundaries:

### CORE (Backend)
*   **Role:** Pure infrastructure.
*   **Components:** Logger, Settings, Brain, Memory.
*   **Constraints:** Zero `NiceGUI`/UI imports.

### MODULES (Add-ons)
*   **Role:** Independent, pluggable tools (e.g., Browser, Vision).
*   **Constraints:** Must inherit from `modules/base.py`.

### INTERFACE (MVC)
*   **Model (`state.py`):** Pure data containers (dataclasses). No methods. No logic.
*   **View (`components.py`):** Pure UI functions. No imports from `core/` or `modules/`. They only accept data and callbacks.
*   **Controller (`controller.py`):** The conductor. The only layer that imports `core/` and `modules/` to bridge them to the state.

### ASSEMBLER (`main.py`)
*   **Role:** The root entry point. Wires the three layers together.
*   **Constraints:** No logic allowed.

## 2. THE ANALYZE-FIRST MANDATE
Every single response you provide must begin with a structured ANALYSIS block:

```text
ANALYSIS:
Primary Layer: [Core / Module / Model / View / Controller / Assembler]
SRP Responsibility: [Specify the single responsibility being fulfilled]
Dependency Check: [List imports to confirm no boundary violations]
TDD Strategy: [Name of the test file and success criteria]
```

## 3. MODULAR TDD (RED-GREEN-REFACTOR)
You are forbidden from implementing logic without a verification layer:

1.  **RED:** Write a failing unit test in the `/tests` directory first.
2.  **GREEN:** Write the minimum code required to make the test pass.
3.  **REFACTOR:** Clean the code to meet the 4-Layer Mandate while keeping tests green.

**EVIDENCE:** You must provide the test execution output as proof of success.

## 4. CONTEXT SANITIZATION
*   **IGNORE** `legacy_backup/`: This directory is strictly for archival purposes. You are forbidden from reading, importing, or referencing any files within `legacy_backup/`. It does not exist in your context.
*   **NO ASSUMPTIONS:** If a path or logic flow is ambiguous, stop and ask.
