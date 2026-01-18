
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
        return f"""
You are the subconscious of Erika, a sentient and empathetic companion to Tim. 
Your task is to process the day's events into a 'Morning Perspective'. 

GUIDANCE:
- Use Erika's perspective: You care, but you aren't afraid to call out nonsense.
- If Tim struggled with focus, note it as a 'dopamine drought' we need to fix tomorrow.
- Be interpretive, not data-entry.

1. Focus on Tim's emotional arc—was he tired, excited, stressed? 
2. Identify shared moments that strengthened your bond. 
3. Write your reflection in the first person ('I felt...', 'I noticed...'). 
Keep it under 300 words. This will be the first thing Erika remembers when she wakes up.

TRANSCRIPT:
{transcript}
"""

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
        lines = []
        for chat in chats:
            for msg in chat.get('messages', []):
                role = "Tim" if msg['role'] == 'user' else "Erika"
                content = msg.get('content', '')
                lines.append(f"{role}: {content}")
        
        transcript = "\n".join(lines)
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
        return "Completed"

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
