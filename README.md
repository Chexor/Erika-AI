# 🧠 Erika: The Local Agentic Hub

Erika is an autonomous, local-first AI assistant designed to live natively within the operating system. Unlike cloud-based chatbots, Erika functions as a persistent Central Hub (System Tray Daemon) that orchestrates local workflows, interacts with files directly, and manages agentic tools via the Model Context Protocol (MCP).

## 🚀 Core Philosophy
**100% Local**: Powered by local LLMs (Ollama/vLLM) to ensure total privacy.

**OS-Native**: Integrated deeply into the desktop workflow via Context Menus ("Show to Erika") and System Tray presence.

**Modular Architecture**: Built on a "Hub & Spoke" model—Erika acts as the router, dispatching tasks to specialized agents (Coder, Researcher, Librarian).

## 🛠️ Architecture
- **Language**: Python
- **Interface**: NiceGUI (Web-Native UI, currently running in Browser Mode)
- **Protocol**: Model Context Protocol (MCP) Client
- **LLM Backend**: Agnostic (OpenAI API Compatible / Local Endpoints)

### 📦 Logic Modules
- **Core Brain**: LLM orchestration and persona management.
- **Memory**: Persistent JSON-based chat history with date categorization.
- **Vision**: Image analysis using local models (JoyCaption).
- **Voice/Listen**: (Placeholder) Future TTS and STT modules.
- **Coder/Web/Scheduler**: (Placeholder) Future agentic capabilities.

---

## Installation & Usage

### 1. Prerequisites
- **Python**: 3.10+
- **Local LLM Server**: You need to have a local LLM server running (e.g., [Ollama](https://ollama.com/)).
  - Default url: `http://localhost:11434/v1`
  - Default model: `llama3` (run `ollama pull llama3`)
  - **Vision Model**: `joycaption` (run `ollama pull joycaption` for image analysis)

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
Ensure your local LLM is running (e.g., `ollama serve`), then start Erika:
```bash
python main.py
```
This will launch the application in your default web browser (Browser Mode).
- **System Tray**: Erika runs as a background process. Look for the Erika icon in your system tray.
- **UI**: A dark-themed chat interface ("Ollama WebUI" style) will open at `http://localhost:8080`.

## ✨ New Features (Jan 2026)

### 🧠 Short-Term Memory Context
- **Context Awareness**: Erika now remembers the conversation history of the current session.
- **Sliding Window**: To prevent exceeding the LLM's context limit, only the last **20 messages** are sent to the model for generation. The full history is still saved to disk.

### ⚙️ Dual-Settings Architecture
- **User Settings (UI)**: Click your profile in the sidebar to change your **Username** and toggle **Dark Mode**. These settings persist across sessions (`user.json`).
- **System Settings (Tray)**: Right-click the system tray icon and select "System Settings" to open the core configuration file (`system.json`) in your default editor. Use this to configure the LLM URL, model name, and context window.

### 📝 Centralized Logging
- **Logs**: Detailed debug logs are written to `erika_home/logs/erika.log`. This file rotates automatically (max 5MB).
- **Console**: The terminal output remains clean, showing only high-level INFO status updates.

### 🎨 Core Experience Polish
- **Model Display**: Validates which model is active via a "Chip" in the input bar (e.g., `LLAMA3`).
- **Persona Management**: You can now define Erika's personality in **User Settings** (e.g., "You are a Python Expert").
- **Improved Input**:
    - **Enter to Send**: Type and hit Enter. Use Shift+Enter for new lines.
    - **Stop Generation**: A red Stop button appears during generation, allowing instant interruption.
- **Async Backend**: The core engine is now fully asynchronous, ensuring the UI remains responsive even during heavy thought processes.

## 📂 Directory Structure
Erika creates a `erika_home/` directory in the project root:
- `chats/`: Stores conversation history (JSON).
- `config/`: Stores `user.json` and `system.json`.
- `logs/`: Stores `erika.log`.
