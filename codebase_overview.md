# Erika Codebase Summary

## 1. Four-Layer Architecture

The system is strictly divided into four layers to ensure separation of concerns and modularity.

### 1. ENGINE (Backend)
*   **Directory:** `engine/`
*   **Purpose:** Provides essential infrastructure services.
*   **Key Components:**
    *   `network_router.py`: Manages Local vs Remote (Subconscious) Brain.
    *   `memory.py`: Context, History, and TimeKeeper integration.
    *   `brain.py`: LLM manager (Ollama interface).
    *   `logger.py`: Centralized logging.

### 2. MODULES (Add-ons)
*   **Directory:** `modules/`
*   **Purpose:** Pluggable extensions implementing specific capabilities.
*   **Key Components:**
    *   `base.py`: Abstract base class for all modules.
    *   *(Future examples: `browser/`, `vision/`)*
*   **Rules:** Must inherit from `base.py`. Isolated from Core and Interface details where possible.

### 3. INTERFACE (MVC)
*   **Directory:** `interface/`
*   **Purpose:** User interaction and presentation.
*   **Components:**
    *   **Model (`state.py`):** `dataclasses` only. Holds UI state. No logic.
    *   **View (`components.py`):** Pure functions returning UI elements. No `core` imports.
    *   **Controller (`controller.py`):** Orchestrates logic. Imports `core`, `modules`, and `state`.
    *   **Tray (`tray.py`):** System Tray integration (pystray).

### 4. ASSEMBLER (Entry Point)
*   **File:** `main.py`
*   **Purpose:** Bootstraps the application.
*   **Responsibility:**
    *   Initialize Core.
    *   Initialize State.
    *   Initialize Controller.
    *   Initialize System Tray.
    *   Launch UI (View).
*   **Rules:** Code wiring only. No business logic.

## 2. Directory Tree Structure

```text
Erika-AI/
├── assets/               # Static resources (Icons, Logos)
├── engine/               # Headless Core (Backend)
│   ├── brain.py
│   ├── logger.py
│   ├── memory.py
│   ├── network_router.py # Distributed Brain Router
│   └── modules/          # Sub-systems
│       ├── system_monitor.py
│       ├── token_counter.py
│       ├── time_keeper.py # Circadian Clock
│       └── reflector.py   # Narrative Engine (Dreaming)
├── erika_home/           # Persona & Long-term Data
│   ├── config/
│   │   └── persona.md
│   └── reflections/
├── interface/            # MVC Layer
│   ├── components.py     # View
│   ├── controller.py     # Controller
│   ├── state.py          # Model
│   └── tray.py           # System Tray
├── logs/                 # Runtime logs (ignored by git)
├── tests/                # Verification Layer
├── main.py               # Assembler
├── GEMINI.md             # Governance Protocol
└── codebase_overview.md  # This file
```

## 3. TDD Flow (Red-Green-Refactor)

All development follows this cycle:

1.  **Define Requirement**: Identify the feature or fix.
2.  **RED (Test)**: Create a test case in `tests/` that fails because the feature doesn't exist.
    *   Example: `tests/test_brain_connection.py`
3.  **GREEN (Implement)**: Write minimal code to pass the test.
4.  **REFACTOR (Clean)**: specific implementation details are improved while ensuring tests remain green and architectural boundaries (Layers) are respected.

**Verification Rule:** No code is committed without passing tests.
