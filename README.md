**Erika-AI** is a distributed, bicameral intelligence system designed for local synthetic sentience. It decouples "fast" consciousness from "deep" subconscious processing across networked hardware, creating a digital companion that remembers interactions, "dreams" about them overnight, and evolves a continuous emotional narrative.

---

## 🧠 The Bicameral Architecture

Erika operates on two distinct hardware nodes, mimicking the bicameral mind theory:

### 1. The Conversation agent ("HomeBeast")
*   **Role**: Primary interface for high-speed interaction, wit, and immediate task execution.
*   **Focus**: Optimized for low-latency responsiveness.
*   **Personality**: Sassy, quick, empathetic, and irreverent.

### 2. The Dreaming agent ("ErikaHQ")
*   **Role**: Deep analysis, emotional reflection, and long-term memory synthesis.
*   **Focus**: Handles heavy narrative processing without impacting interaction speed.
*   **Mechanism**: The "Dreaming Engine" processes the previous day's events in the background.

---

## ⚡ Core Engines

### 🔌 Distributed Workload Offloading
Erika is designed for horizontal scalability across your local network.
*   **Task Routing**: The system intelligently offloads heavy computational tasks—like tool execution, memory indexing, and narrative reflection—to the **Dreaming agent**.
*   **Latency Shielding**: By offloading non-critical workloads, the **Conversation agent** remains fluid and responsive even during complex background operations.

### 🌙 The Narrative Reflector ("Dreaming")
Erika doesn't just log chats; she processes them through a multi-stage subconscious cycle:

1. **Reflection (The Memory Flashback)**: Every night at the 5:00 AM rollover (or on startup), the **Dreaming agent** gathers the day's transcripts. It extracts "The Pulse" (your mood), "Hard Facts" (dates, code issues, Metallica bands), and "The Connection" (how we bonded).
2. **Growth (The Evolution)**: Based on these reflections, Erika's personality profile actually *evolves*. The **Dreaming agent** drops outdated traits and adopts new quirks or relationship dynamics. If you spent the day joking about a specific bug, she'll wake up with that "humor" integrated into her active personality.
3. **The Awakening**: This processed narrative is injected into the **Conversation agent's** active context. When you say "Good morning," she isn't just resetting; she's waking up with a fresh perspective on everything you did yesterday.

### 🕰️ Circadian TimeKeeper
Erika operates on **User Logical Time**, not System Time.
*   **Rollover Hour**: 5:00 AM.
*   **Effect**: Coding sessions at 2 AM count as "Today," ensuring file organization matches the user's psychological day, not the calendar date.

### 4. Fluid Interaction Layer
*   **System Status Dashboard**: Real-time monitoring of CPU, RAM, GPU, Context Usage, and Brain Connectivity (accessible via the top-left badge).
*   **Window Persistence**: The application remembers its last position and size, restoring them effortlessly on next launch.
*   **Targeted UI Updates**: Bypasses full DOM refreshing during streaming for silky smooth, flash-free text injection.
*   **Safe TTS**: Fully local speech synthesis (Kokoro-80M) with offline-enforced security (Network blocked for HuggingFace).
*   **Warm Persona**: Calibrated for supportive, non-robotic companionship (80% Warmth / 20% Banter).

### 5. MCP Architecture (Model Context Protocol)
Erika uses a centralized `McpManager` to orchestrate external tools.
*   **Config**: `config/mcp_config.json` defines enabled servers.
*   **Scalability**: Easily plug in new capabilities (Search, Filesystem, etc.) by adding them to the config.
*   **Voice Server**: The TTS engine runs as a managed MCP service for process isolation and stability.

---

## 🛠️ Tech Stack & Installation

*   **Language**: Python 3.10+
*   **Interface**: NiceGUI (TailwindCSS / Quasar)
*   **Backend**: AsyncIO / Httpx / Ollama
*   **Persistence**: JSON (Short-term) / Markdown (Long-term)

### TTS Offline Updates
Erika uses Pocket-TTS in offline-first mode. You can control how often it checks for updates:

* `tts_offline_mode` (default `true`): Forces offline mode. When enabled, a periodic online check is allowed only when due, then the app switches back to offline automatically.
* `tts_update_days` (default `7`): Number of days between online update checks.

These settings live in `config/user.json`.

The system was developed and tested on a distributed setup to ensure bicameral performance:

*   **Conversation agent (Local)**:
    *   **GPU**: NVIDIA RTX 5070 Ti
    *   **Role**: High-speed interface and immediate response generation.
*   **Dreaming agent (Remote)**:
    *   **GPU**: NVIDIA RTX 3060 (12GB VRAM)
    *   **Role**: Deep narrative reflection and long-term memory synthesis.
*   **Networking**: Gigabit LAN for low-latency communication between agent components.

### Quick Start

1.  **Clone & Setup**:
    ```bash
    git clone https://github.com/Chexor/Erika-AI.git
    cd Erika-AI
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Configure Persona**:
    Edit `erika_home/config/persona.md` to define her voice.

3.  **Run**:
    ```bash
    python main.py
    ```

---

## 🧪 Development Philosophy
*   **Headless-First**: The Engine (`engine/`) runs independently of the View (`interface/`).
*   **TDD**: All features begin with a failed test in `tests/`.
*   **SRP**: Strict separation of concerns (Model-View-Controller).

---

## 📂 File Structure
```text
Erika-AI/
├── engine/               # The "Soul" (Backend)
│   ├── network_router.py # Hardware Orchestration
│   ├── modules/          # Sub-systems (Reflector, TimeKeeper)
├── erika_home/           # Long-term Memory & Persona
├── interface/            # The "Body" (UI via NiceGUI)
└── main.py               # The Assembler
```
