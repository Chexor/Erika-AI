# Erika AI

**Erika AI** is a modular, local-first AI assistant built with Python. It features a strict Four-Layer Architecture (Core, Modules, Interface, Assembler) and uses NiceGUI for a modern, reactive web interface.

## Features
*   **Local LLM**: Powered by [Ollama](https://ollama.com).
*   **Modern UI**: Built with NiceGUI & Tailwind CSS. Dark mode by default.
*   **System Tray**: Native OS integration for background running and quick access.
*   **Persistent Memory**: Chat history and settings saved locally (JSON).
*   **Modular Architecture**: Designed for pluggable extensions (Web, Vision, Voice).

## Requirements
*   **Python 3.10+**
*   **Ollama**: Installed and running (`ollama serve`).
*   **Models**: Pull a model (e.g., `ollama pull llama3`).

## Quick Start

1.  **Clone & Setup**:
    ```bash
    git clone <repo-url>
    cd Erika-AI
    python -m venv .venv
    .venv\Scripts\activate   # Windows
    pip install -r requirements.txt
    ```

2.  **Run**:
    ```bash
    python main.py
    ```
    The application will launch in your default browser at `http://localhost:8080`.
    A system tray icon will appear for background control.

## Architecture
See [codebase_overview.md](codebase_overview.md) for detailed architectural documentation.

## Development
This project follows a strict **TDD (Red-Green-Refactor)** workflow.
*   **Run Tests**:
    ```bash
    python -m unittest discover tests/
    ```
*   **Logs**: Check `logs/erika_debug.log` for runtime details.

## Recent Updates
*   **System Tray**: Added "Open WebUI" and "Quit" options.
*   **UI Polish**: Custom avatar, absolute positioning for input area.
*   **Stability**: Fixed async event handling and log bloat issues.
