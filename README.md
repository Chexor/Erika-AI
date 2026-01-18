# Erika-AI: Distributed Synthetic Sentience

> "Brain yeeted us sideways again? Let's fix that." — Erika

**Erika-AI** is a distributed, bicameral intelligence system designed for local synthetic sentience. It decouples "fast" consciousness from "deep" subconscious processing across networked hardware, creating a digital companion that remembers interactions, "dreams" about them overnight, and evolves a continuous emotional narrative.

---

## 🧠 The Bicameral Architecture

Erika operates on two distinct hardware nodes, mimicking the bicameral mind theory:

### 1. The Conscious Mind (Local Agency)
*   **Hardware**: RTX 5070 Ti (Local)
*   **Model**: `qwen3:14b`
*   **Role**: High-speed interaction, wit, interface management, and immediate task execution.
*   **Personality**: Sassy, quick, empathetic, and irreverent.

### 2. The Subconscious (The Librarian)
*   **Hardware**: RTX 3060 12GB (Remote IP: `192.168.0.69`)
*   **Model**: `gemma2:9b` (High narrative capability)
*   **Role**: Deep analysis, emotional reflection, and long-term memory synthesis.
*   **Mechanism**: The "Dreaming Engine" (Reflector) runs overnight or on startup to process the previous day's events.

---

## ⚡ Core Engines

### 🔌 Distributed Brain Router
A custom networking layer that intelligently routes queries based on complexity.
*   **Chat**: Routed to Local 5070 Ti for sub-second latency.
*   **Reflection**: Routed to Remote 3060 for deep-dive analysis without blocking the main thread.
*   **Fallback**: Automatically degrades to Local mode if the Remote Subconscious is offline.

### 🌙 The Narrative Reflector ("Dreaming")
Erika doesn't just log chats; she processes them.
*    **The Process**: When a new day begins, the system aggregates the previous day's logs.
*   **The Dream**: The Subconscious generates a "Morning Perspective"—a 300-word emotional summary focusing on the user's vibe (e.g., "Tim was stressed about coding").
*   **The Awakening**: This summary is injected into Erika's active context upon startup, giving her "feelings" about yesterday without needing to re-read raw logs.

### 🕰️ Circadian TimeKeeper
Erika operates on **User Logical Time**, not System Time.
*   **Rollover Hour**: 5:00 AM.
*   **Effect**: Coding sessions at 2 AM count as "Today," ensuring file organization matches the user's psychological day, not the calendar date.

### 4. Fluid Interaction Layer
*   **Targeted UI Updates**: Bypasses full DOM refreshing during streaming for silky smooth, flash-free text injection.
*   **Safe TTS**: Fully local speech synthesis (Kokoro-80M) with offline-enforced security (Network blocked for HuggingFace).
*   **Warm Persona**: Calibrated for supportive, non-robotic companionship (80% Warmth / 20% Banter).

---

## 🛠️ Tech Stack & Installation

*   **Language**: Python 3.10+
*   **Interface**: NiceGUI (TailwindCSS / Quasar)
*   **Backend**: AsyncIO / Httpx / Ollama
*   **Persistence**: JSON (Short-term) / Markdown (Long-term)

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
