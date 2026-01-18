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
*   **Directory:** `engine/modules/`
*   **Purpose:** Pluggable extensions implementing specific capabilities.
*   **Key Components:**
    *   `reflector.py`: Manages Daily Reflections and Personality Evolution.
    *   `time_keeper.py`: Enforces the 5 AM logical day rollover.

### 3. INTERFACE (MVC)
*   **Directory:** `interface/`
*   **Purpose:** User interaction and presentation via NiceGUI.
*   **Components:**
    *   **View (`view.py`):** Pure UI definitions and layout logic.
    *   **Controller (`controller.py`):** The Brain. Orchestrates logic, holds state, manages the event loop.
    *   **Settings (`settings_ui.py`):** Logic for the settings modal.
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
│       └── reflector.py   # Narrative Engine (Reflections & Growth)
├── erika_home/           # Persona & Long-term Data
│   ├── config/
│   │   ├── system_core.md   # The Law (TTS Safety)
│   │   ├── erika_soul.md    # The Vibe (User Settings)
│   │   └── erika_growth.md  # The Journey (Auto-Evolving)
│   └── reflections/
├── interface/            # MVC Layer
│   ├── view.py           # View (NiceGUI Components)
│   ├── controller.py     # Controller (Logic & State)
│   ├── settings_ui.py    # Settings Modal
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
