# Gemini Context: Erika AI Assistant

This document provides a summary of the Erika AI assistant project to give context for future development and maintenance.

## 1. Project Overview

Erika is a local-first, autonomous AI assistant designed to run natively on a desktop operating system. It functions as a persistent system tray application that provides a chat interface to a locally running Large Language Model (LLM).

**Core Technologies:**
- **Language:** Python
- **UI:** [NiceGUI](https://nicegui.io/) for the web-based UI, wrapped in a native desktop window using [pywebview](https://pywebview.flowrl.com/).
- **System Integration:** [pystray](https://pystray.readthedocs.io/) for the system tray icon and menu.
- **LLM Backend:** Interacts with any OpenAI API-compatible local LLM server, such as [Ollama](https://ollama.com/) or vLLM.

**Architecture:**
- `main.py`: The main entry point. It initializes and runs the system tray icon in a background thread and starts the NiceGUI user interface.
- `interface/ui.py`: Defines the chat interface using NiceGUI. It runs in a native window.
- `core/brain.py`: Contains the central `Brain` class that manages the AI's persona and orchestrates calls to the LLM engine. LLM configuration (endpoint URL and model name) is currently hardcoded here.
- `core/llm/engine.py`: Implements the `LocalLLMEngine` which handles the actual communication with the local LLM server via the `openai` Python client. It supports both blocking and streaming responses.
- `scripts/`: Contains utility and test scripts.

## 2. Building and Running

### Prerequisites
1.  **Python 3.10+**
2.  **Local LLM Server:** An OpenAI-compatible server like Ollama must be running.
    - Default Endpoint: `http://localhost:11434/v1`
    - Default Model: `llama3` (can be changed in `core/brain.py`)

### Installation
Install the required Python dependencies from the project root:
```bash
pip install -r requirements.txt
```

### Running the Application
To start the Erika assistant, run the following command from the project root:
```bash
python main.py
```
This will launch the UI and add an icon to the system tray.

## 3. Testing

The project contains a simple test script to verify the core `Brain` functionality without launching the full UI.

To run the test:
```bash
python scripts/test_brain.py
```
This script will initialize the `Brain`, send a test prompt, and print the LLM's response, testing both standard and streaming generation.

## 4. Development Conventions

- **Modular Structure:** The code is separated by concern into `core` (business logic), `interface` (UI), and `scripts` (utilities).
- **Configuration:** Key configuration like the LLM endpoint is currently hardcoded in `core/brain.py`. A good improvement would be to move this to a separate configuration file (e.g., `config.py`, `.env`).
- **LLM Abstraction:** The `LocalLLMEngine` inherits from a `LLMProvider` base class, which suggests an intention to potentially support different LLM backends in the future.
- **Error Handling:** The LLM engine includes basic error handling to inform the user if the local AI server is not reachable.
