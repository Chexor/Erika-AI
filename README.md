# 🧠 Erika: The Local Agentic Hub

Erika is an autonomous, local-first AI assistant designed to live natively within the operating system. Unlike cloud-based chatbots, Erika functions as a persistent Central Hub (System Tray Daemon) that orchestrates local workflows, interacts with files directly, and manages agentic tools via the Model Context Protocol (MCP).

## 🚀 Core Philosophy
**100% Local**: Powered by local LLMs (Ollama/vLLM) to ensure total privacy.

**OS-Native**: Integrated deeply into the desktop workflow via Context Menus ("Show to Erika") and System Tray presence.

**Modular Architecture**: Built on a "Hub & Spoke" model—Erika acts as the router, dispatching tasks to specialized agents (Coder, Researcher, Librarian).

## 🛠️ Architecture
- **Language**: Python
- **Interface**: NiceGUI / Streamlit (Local Web-Native UI)
- **Protocol**: Model Context Protocol (MCP) Client
- **LLM Backend**: Agnostic (OpenAI API Compatible / Local Endpoints)

---

## Installation & Usage

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```
