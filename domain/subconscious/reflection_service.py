import os
import datetime
import logging
import logging

logger = logging.getLogger("domain.subconscious.reflection")

class ReflectionService:
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
            "- **NO ROBOT POETRY**: Do not talk about 'circuits', 'data streams', or 'digital hearts'. You are a girl sitting at a computer.\n"
            "- EXTRACT FACTS: If he mentioned a specific band or project, WRITE IT DOWN."
        )

    async def reflect_on_day(self, date_obj: datetime.date) -> tuple[str, str | None]:
        """
        Runs the reflection process for the given date.
        Returns: (status, content)
        """
        date_str = date_obj.strftime('%d-%m-%Y')
        logger.info(f"ReflectionService: Starting reflection for {date_str}")
        
        # 1. Determine Brain (Lucid Dreaming Upgrade)
        # Prefer Remote (Deep Thought), but fall back to Local (Subconscious) if offline.
        remote_online = self.router.status.get('remote')
        
        target_host = self.router.REMOTE_BRAIN if remote_online else self.router.LOCAL_BRAIN
        target_model = self.router.REMOTE_MODEL if remote_online else self.router.LOCAL_MODEL
        
        logger.info(f"ReflectionService: Dreaming via {'Remote' if remote_online else 'Local (Erika Core)'} [{target_model}]")

        # 2. Get Data
        chats = self.memory.get_chats_by_date(date_obj)
        if not chats:
            logger.info("ReflectionService: No chats found for this date. Skipping.")
            return "No Data", None

        # 3. Build Transcript
        transcript = self._build_transcript(chats)
        if not transcript: 
            return "No Data", None

        # 4. Generate
        prompt = self._generate_prompt(transcript)
        
        full_response = ""
        generation_error = False
        
        try:
            async for chunk in self.brain.generate_response(
                model=target_model, 
                messages=[{"role": "user", "content": prompt}], 
                host=target_host
            ):
                if "error" in chunk:
                     logger.error(f"ReflectionService: Brain returned error: {chunk['error']}")
                     generation_error = True
                     break
                     
                if "message" in chunk:
                    full_response += chunk['message'].get('content', '')
                    
            # Check for validation failures
            if generation_error:
                return "Failed", None
            if not full_response or not full_response.strip():
                logger.warning("ReflectionService: Generated content came back empty. Aborting save.")
                return "Failed", None
                
        except Exception as e:
            logger.error(f"ReflectionService: Generation failed: {e}")
            return "Failed", None
            
        # 5. Save
        filename = f"day_{date_str}.md"
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# Morning Perspective: {date_str}\n\n{full_response}")
            logger.info(f"ReflectionService: Reflection saved to {filename}")
            return "Completed", full_response
        except Exception as e:
            logger.error(f"ReflectionService: Failed to save file: {e}")
            return "Failed", None

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
            logger.error(f"ReflectionService: Failed to read latest reflection: {e}")
            return ""
