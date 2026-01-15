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

---

## Installation & Usage

### 1. Prerequisites
- **Python**: 3.10+
- **Local LLM Server**: You need to have a local LLM server running (e.g., [Ollama](https://ollama.com/)).
  - Default url: `http://localhost:11434/v1`
  - Default model: `llama3` (run `ollama pull llama3`)

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
