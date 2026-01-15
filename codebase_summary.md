# Erika AI Codebase Summary

This document provides a comprehensive overview of the Erika AI architecture, designed for reporting to the "Architect" Gem.

## 1. Project Overview
**Erika** is a local-first, OS-integrated AI assistant. She functions as a central hub for desktop automation, powered by local LLMs and modular agents.
- **Philosophy**: Privacy-first, OS-native integration, Modular "Hub & Spoke" architecture.
- **Current Status**: MVP Scaffolding complete with Brain Module connected to Local LLM.

## 2. Architecture & Tech Stack

| Component | Technology | functionality |
|:--- |:--- |:--- |
| **Language** | Python 3.10+ | Core logic and orchestration. |
| **Interface** | NiceGUI | Web-based native UI (pywebview) for chat. |
| **System Integration** | pystray | System Tray icon and background persistence. |
| **Brain / LLM** | OpenAI Client / Adapter | Connects to local inference servers (Ollama/vLLM). |

## 3. Directory Structure

```text
Erika-AI/
├── main.py                 # Entry point (System Tray + UI Launcher)
├── requirements.txt        # Dependencies (nicegui, pystray, openai, etc.)
├── core/                   # The "Brain" of the operation
│   ├── brain.py            # Main orchestration class (Brain)
│   └── llm/                # LLM Adapter Module
│       ├── base.py         # Abstract Base Class (LLMProvider)
│       └── engine.py       # Concrete Implementation (LocalLLMEngine)
├── interface/              # User Interface
│   └── ui.py               # NiceGUI Chat Layout and Event Handlers
├── erika_home/             # Local storage (Memory, Logs - Placeholder)
└── scripts/                # Utilities
    └── test_brain.py       # Verification script for LLM connection
```

## 4. Key Components Detail

### Core: `core/brain.py`
The `Brain` class acts as the central coordinator. It currently initializes the `LocalLLMEngine` and routes user input to the LLM. It maintains the system persona ("You are Erika...").

### LLM Module: `core/llm/`
Implements the **Adapter Pattern** to decouple the rest of the application from specific LLM providers.
- `LLMProvider` (ABC): Defines the contract (`generate`, `stream`).
- `LocalLLMEngine`: Connects to `localhost:11434/v1` (Ollama default) using the `openai` Python client.

### Interface: `interface/ui.py`
A reactive web UI built with **NiceGUI**.
- Features a chat container with "You" and "Erika" messages.
- Calls `core.brain.process_input` (mapped to `Brain.think` in later iterations) to get responses.
- Runs in "Native" mode (using pywebview) to appear as a desktop application window.

### Entry Point: `main.py`
- Runs the `pystray` icon in a separate thread.
- Launches the NiceGUI main thread.
- Provides context menu options: "Open Erika", "Exit".

## 5. Next Steps for Development
1. **Memory System**: Implement `erika_home` JSON storage for persistent conversation history.
2. **Context Awareness**: Add ability to read clipboard or selected text.
3. **MCP Integration**: Connect to the Model Context Protocol to drive external tools.
