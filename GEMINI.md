# Gemini Context: Erika AI Assistant

This document provides a summary of the Erika AI assistant project to give context for future development and maintenance.

## 1. Project Overview

Erika is a local-first, autonomous AI assistant designed to run natively on a desktop operating system. It functions as a persistent system tray application that provides a chat interface to a locally running Large Language Model (LLM).

**Core Technologies:**
- **Language:** Python 3.10+
- **UI:** [NiceGUI](https://nicegui.io/) (Web-Native).
- **Architecture:** Strict MVC (Model-View-Controller).
- **System Integration:** [pystray](https://pystray.readthedocs.io/) (System Tray).
- **LLM Backend:** [Ollama](https://ollama.com/) (Local).

**Architecture:**
- `main.py`: Bootstrapper. Starts Tray and UI.
- `interface/state.py` (Model): Reactive data container.
- `interface/components.py` (View): Pure UI functions.
- `interface/controller.py` (Controller): Business logic & Orchestration.
- `core/brain.py`: Singleton LLM manager.
- `core/settings.py`: Dual-config manager (`user.json` / `system.json`).
- `erika_home/`: User data directory (Chats, Logs, Config).

## 2. Building and Running

### Prerequisites
1.  **Python 3.10+**
2.  **Ollama**: Must be installed.

### Installation
```bash
pip install -r requirements.txt
```

### Running
Double-click `launch_erika.bat` OR run:
```bash
python main.py
```
-   **UI**: `http://localhost:8080`
-   **Tray**: Right-click for System Settings.

## 3. Development Conventions

-   **Strict SRP**:
    -   **View** never imports `core`.
    -   **Controller** never imports `nicegui.ui` (except for specific type hints if needed, but logic should be pure).
-   **Configuration**: All config lives in `erika_home/config/`. Do NOT hardcode paths.
-   **Logging**: Use `core.logger.setup_logger`. Never `print()`. Logs go to `erika_home/logs/`.
-   **State**: All UI state must live in `AppState` inside `interface/state.py`.
