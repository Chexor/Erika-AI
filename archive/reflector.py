
import os
import datetime
import logging
from engine.logger import setup_engine_logger

logger = setup_engine_logger("ENGINE.Reflector")

class Reflector:
    def __init__(self, brain, memory, router):
        self.brain = brain
        self.memory = memory
        self.router = router
        self.output_dir = os.path.join("erika_home", "reflections")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _generate_prompt(self, transcript: str) -> str:
        return (
            "You are the subconscious of Erika, an AI companion. "
            "Below is a transcript of your interactions with Tim today.\n\n"
            f"TRANSCRIPT:\n{transcript}\n\n"
            "TASK:\n"
            "Write a concise, grounded diary entry (max 250 words) determining what matters from today. "
            "Use the following structure exactly:\n"
            "1. **The Pulse**: How was Tim actually doing? (e.g., tired, hyperfocused, stressed).\n"
            "2. **The Hard Facts**: List specific things Tim mentioned (projects, code issues, names, dates, bands, hobbies). "
            "Be specific (e.g., 'He mentioned Metallica' not 'He liked music').\n"
            "3. **The Connection**: What was our 'vibe' today? Did we bond over something specific?\n"
            "4. **Tomorrow's Hook**: One specific thing to follow up on or remember for tomorrow.\n\n"
            "CONSTRAINTS:\n"
            "- Tone: Casual, specific, grounded. Use 'I' and 'We'.\n"
            "- NO FLOWERY METAPHORS: Avoid phrases like 'invisible currents' or 'code and circuits'.\n"
            "- EXTRACT FACTS: If he mentioned a specific band or project, WRITE IT DOWN."
        )

    async def reflect_on_day(self, date_obj: datetime.date) -> str:
        """Runs the reflection process for the given date."""
        date_str = date_obj.strftime('%d-%m-%Y')
        logger.info(f"Reflector: Starting reflection for {date_str}")
        
        # 1. Check Router (Strictly Remote)
        if not self.router.status.get('remote'):
            logger.warning("Reflector: Erika's Subconscious (Remote) offline. Task Pending.")
            return "Pending"

        # 2. Get Data
        chats = self.memory.get_chats_by_date(date_obj)
        if not chats:
            logger.info("Reflector: No chats found for this date. Skipping.")
            return "No Data"

        # 3. Build Transcript
        transcript = self._build_transcript(chats)
        if not transcript: 
            return "No Data"

        # 4. Generate
        prompt = self._generate_prompt(transcript)
        # Use Remote Host explicitly
        remote_host = self.router.REMOTE_BRAIN 
        remote_model = self.router.REMOTE_MODEL
        
        full_response = ""
        try:
            # We use the brain to generate, forcing the host to the Librarian
            async for chunk in self.brain.generate_response(
                model=remote_model, 
                messages=[{"role": "user", "content": prompt}], 
                host=remote_host
            ):
                if "message" in chunk:
                    full_response += chunk['message'].get('content', '')
        except Exception as e:
            logger.error(f"Reflector: Generation failed: {e}")
            return "Failed"
            
        # 5. Save
        filename = f"day_{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Morning Perspective: {date_str}\n\n{full_response}")
            
        logger.info(f"Reflector: Reflection saved to {filename}")
        
        # 6. Evolve Personality
        await self.evolve_personality(full_response)
        
        return "Completed"

    async def evolve_personality(self, latest_reflection: str):
        """Updates the living personality profile based on recent growth."""
        logger.info("Reflector: Evolving personality...")
        
        growth_path = os.path.join("erika_home", "config", "erika_growth.md")
        current_growth = ""
        if os.path.exists(growth_path):
             with open(growth_path, 'r', encoding='utf-8') as f:
                 current_growth = f.read()

        prompt = (
            "You are updating the 'Growth' segment of Erika's personality. "
            "This document tracks how you are evolving based on your experiences with Tim.\n\n"
            f"PREVIOUS GROWTH STATE:\n{current_growth}\n\n"
            f"LATEST REFLECTION:\n{latest_reflection}\n\n"
            "TASK:\n"
            "Rewrite the Growth Profile (max 150 words). "
            "Drop outdated traits. Add new quirks or relationship dynamics derived from the latest reflection. "
            "Format as a list of bullet points under headers.\n\n"
            "OUTPUT FORMAT:\n"
            "### EVOLVING TRAITS ###\n"
            "- **Current Mood**: [Summary]\n"
            "- **New Humor/Quirks**: [e.g. references to specific bands/jokes]\n"
            "- **Dynamic**: [How you relate to Tim right now]"
        )

        # Generate - Use Remote 
        remote_host = self.router.REMOTE_BRAIN 
        remote_model = self.router.REMOTE_MODEL
        
        new_growth = ""
        try:
            async for chunk in self.brain.generate_response(
                model=remote_model, 
                messages=[{"role": "user", "content": prompt}], 
                host=remote_host
            ):
                if "message" in chunk:
                    new_growth += chunk['message'].get('content', '')
            
            # Save
            if new_growth:
                 os.makedirs(os.path.dirname(growth_path), exist_ok=True)
                 with open(growth_path, 'w', encoding='utf-8') as f:
                     f.write(new_growth)
                 logger.info("Reflector: Personality Evolved.")
                 
        except Exception as e:
            logger.error(f"Reflector: Evolution failed: {e}")

    def _build_transcript(self, chats: list) -> str:
        """Helper to flatten chats into a text transcript."""
        lines = []
        for chat in chats:
            for msg in chat.get('messages', []):
                role = "Tim" if msg['role'] == 'user' else "Erika"
                content = msg.get('content', '')
                lines.append(f"{role}: {content}")
        return "\n".join(lines)

    def get_latest_reflection(self) -> str:
        """Retrieves the most recent reflection content."""
        if not os.path.exists(self.output_dir):
            return ""
            
        try:
            files = [f for f in os.listdir(self.output_dir) if f.endswith(".md")]
            if not files:
                return ""
            
            # Sort by name (day_DD-MM-YYYY.md)
            latest_file = None
            latest_date = None
            
            for f in files:
                try:
                    # Remove 'day_' and '.md'
                    date_part = f[4:-3]
                    dt = datetime.datetime.strptime(date_part, '%d-%m-%Y').date()
                    if latest_date is None or dt > latest_date:
                        latest_date = dt
                        latest_file = f
                except ValueError:
                    continue
            
            if latest_file:
                path = os.path.join(self.output_dir, latest_file)
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
            return ""
        except Exception as e:
            logger.error(f"Reflector: Failed to read latest reflection: {e}")
            return ""
