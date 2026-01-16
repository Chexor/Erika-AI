# 🧠 Erika: The Local Agentic Hub

Erika is an autonomous, local-first AI assistant designed to live natively within the operating system. functions as a persistent Central Hub (System Tray Daemon) that orchestrates local workflows.

## 🚀 Core Philosophy
**100% Local**: Powered by local LLMs (Ollama/vLLM) to ensure total privacy.

**OS-Native**: Integrated deeply into the desktop workflow via System Tray presence.

**Modular Architecture**: Built on a strict **MVC (Model-View-Controller)** pattern for robustness and scalability.

## 🛠️ Architecture
- **Language**: Python 3.10+
- **UI Framework**: NiceGUI (Web-Native)
- **Design Pattern**: Strict MVC

### 📦 Logic Modules
-   **Model (`interface/state.py`)**: Reactive data container. The Single Source of Truth.
-   **View (`interface/components.py`)**: Pure UI rendering. Clean, stateless components.
-   **Controller (`interface/controller.py`)**: The application brain. Manages `state`, `Brain`, `Memory`, and `Settings`.
-   **Core Brain**: LLM orchestration.
-   **Memory**: Persistent JSON-based chat history.
-   **Vision**: Image analysis using local models (JoyCaption).

---

## Installation & Usage

### 1. Prerequisites
-   **Python**: 3.10+
-   **Local LLM Server**: (e.g., [Ollama](https://ollama.com/)).
    -   Default url: `http://localhost:11434/v1`
    -   Default model: `llama3`
    -   **Vision Model**: `joycaption` (optional)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python main.py
```
-   **UI**: Opens at `http://localhost:8080`.
-   **System Tray**: Background process management.

## ✨ New Features (Refactored)

### 🏗️ Strict MVC Architecture
The codebase has been refactored to decouple logic from the UI.
-   **Stable**: Changing UI libraries won't break logic.
-   **Clean**: No more spaghetti code or circular dependencies.

### 🛡️ Robust Logging
-   **Centralized**: All logs (Application, Brain, Async) go to `erika_home/logs/erika_debug.log`.
-   **Rotated**: Logs rotate automatically (5MB limit) to save space.

### 🛑 Graceful Shutdown
-   The application now cleans up resources and threads properly when stopped via the UI or Ctrl+C.

## 📂 Directory Structure
-   `core/`: Backend logic (Brain, Memory, Logger, LLM Engine).
-   `interface/`: Frontend logic (MVC).
    -   `state.py`: Model.
    -   `controller.py`: Controller.
    -   `components.py`: View.
    -   `main.py`: Assembler.
-   `erika_home/`: User data (Chats, Config, Logs).

