# Erika AI Codebase Summary

**Version**: 2.0 (MVC Refactor)
**Date**: Jan 2026
**Architecture**: Strict MVC / Local-First

This document acts as the technical bible for the Erika AI project. It details the architectural decisions, component responsibilities, and data flows of the system.

---

## 1. Project Philosophy
Erika is more than a chatbot; she is an **OS-Native Agentic Hub**.
*   **Local-First**: Zero data exfiltration. All inference happens on `localhost`.
*   **OS-Integrated**: Persists in the System Tray, minimizing to background, ready to be summoned.
*   **Strict Separation**: Identifying that UI libraries change often, we enforce a strict separation between Logic (Controller) and Presentation (View).

---

## 2. High-Level Architecture
The application follows a **Strict MVC (Model-View-Controller)** pattern, assembled by a Dependency Injection-style entry point.

| Layer | Component | Responsibility | Dependencies |
| :--- | :--- | :--- | :--- |
| **Model** | `interface/state.py` | Holds the **Reactive State**. Single Source of Truth. | None |
| **View** | `interface/components.py` | **Pure Functions**. Renders UI based on Data & Callbacks. | None (Strict) |
| **Controller** | `interface/controller.py` | **Business Logic**. Manipulates State, calls Internal APIs. | `core.*`, `state` |
| **Assembler** | `interface/main.py` | **Wiring**. Initializes MVC, injects dependencies, handles Layout. | All of the above |
| **Backend** | `core/*` | **Infrastructure**. LLM, Memory, Logging, Config. | External Libs |

---

## 3. Component Deep Dive

### A. The Interface Layer (`interface/`)

#### 1. `state.py` (The Model)
A naive data container that holds the application state. It performs no logic other than basic list appends.
*   **Key Properties**:
    *   `messages` (List[Dict]): The live chat history.
    *   `is_generating` (Bool): Controls UI loading states.
    *   `sidebar_history` (Dict): Grouped list of past chats.
    *   `notifications` (List): Queue for toast messages.

#### 2. `components.py` (The View)
A library of "dumb" UI components. They do not know about the database, the network, or the brain.
*   **`ChatBubble`**: Renders a message. Takes `on_regenerate`, `on_copy` callbacks.
*   **`InputBar`**: Renders the text area. Takes `on_send`, `on_stop` callbacks.
*   **`Sidebar`**: Renders the history list. Takes `on_load_chat`, `on_new_chat`.

#### 3. `controller.py` (The Controller)
The brains of the operation. It orchestrates the flow of data.
*   **`handle_send(text)`**:
    1.  Updates `state` immediately (Optimistic UI).
    2.  Calls `core.brain.think_stream`.
    3.  Updates `state` with streaming chunks.
    4.  Saves result to `core.memory`.
*   **`shutdown()`**: Ensures graceful cleanup of threads and resources.
*   **Dependencies**: It is the **ONLY** class allowed to import `core.brain` or `core.memory`.

#### 4. `main.py` (The Assembler)
The entry point for the UI process.
*   Initializes `AppState`.
*   Initializes `ErikaController(state)`.
*   Defines `ui.refreshable` zones to react to state changes.
*   **Wiring**: Creates functions like `on_send_click` that bridge the View's events to the Controller's logic.

---

### B. The Core Layer (`core/`)

#### 1. `brain.py` (The Intelligence)
A **Singleton** orchestrator for the LLM.
*   **Role**: Manages the connection to the Local LLM (Ollama).
*   **Status Check**: Verifies LLM health on startup.
*   **Persona**: Injects the System Prompt defined in `user.json`.

#### 2. `memory.py` (The Storage)
Handles persistence of chat history.
*   **Format**: JSON files stored in `erika_home/chats/`.
*   **Schema**:
    ```json
    {
      "id": "uuid",
      "title": "Conversation Title",
      "messages": [ {"role": "user", "content": "..."} ]
    }
    ```

#### 3. `logger.py` (The Watchdog)
Provides robust, centralized logging.
*   **Destination**: `erika_home/logs/erika_debug.log`.
*   **Rotation**: Max 5MB, 5 Backups.
*   **Transformation**: Hooks `sys.excepthook` and `asyncio.loop.set_exception_handler` to catch "silent" crashes.

#### 4. `settings.py` (The Configuration)
Manages the dual-configuration system.
*   `user.json`: User preferences (Theme, Name, Personal Custom Instructions).
*   `system.json`: Technical config (Ollama URL, Model Name, Context Window).

---

## 4. Data Flow Walkthrough: "User Sends a Message"

1.  **User Interaction**: User types "Hello" and clicks Send in `InputBar`.
2.  **View Event**: `InputBar` fires the `on_send("Hello")` callback provided by `main.py`.
3.  **Assembler Relay**: `main.py` calls `controller.handle_send("Hello")`.
4.  **Controller Logic**:
    *   **Optimistic Update**: Appends "Hello" and a "..." placeholder to `state.messages`.
    *   **UI Refresh**: `state` change triggers `ui.refreshable` in `main.py`. User sees the message instantly.
    *   **Inference**: Controller calls `brain.think_stream()`.
    *   **Streaming**: As chunks arrive, Controller updates the last message in `state`.
    *   **Live UI**: `main.py` (via a Timer/Hook) pushes the text update to the DOM.
5.  **Persistence**: Controller calls `memory.save_turn()`.
6.  **Completion**: Controller sets `state.is_generating = False`. UI updates to show "Ready" state.

---

## 5. Directory Verification

```text
Erika-AI/
├── launch_erika.bat        # Launcher (Ollama check + Venv + Run)
├── main.py                 # Application Bootstrap
├── requirements.txt        # Python Dependencies
├── core/
│   ├── brain.py
│   ├── logger.py
│   ├── memory.py
│   └── settings.py
├── interface/
│   ├── components.py       # Pure View
│   ├── controller.py       # Business Logic
│   ├── main.py             # UI Assembly
│   ├── settings_ui.py      # Settings Component
│   ├── state.py            # Reactive Model
│   └── tray.py             # System Tray
└── erika_home/             # (Ignored by Git)
    ├── chats/              # JSON History
    ├── config/             # User/System Config
    └── logs/               # Debug Logs
```