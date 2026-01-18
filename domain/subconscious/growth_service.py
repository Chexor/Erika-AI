import os
import logging
from engine.logger import setup_engine_logger

# Setup Domain Logger
logger = setup_engine_logger("DOMAIN.GrowthService")

class GrowthService:
    def __init__(self, brain, router):
        self.brain = brain
        self.router = router
        self.config_dir = os.path.join("erika_home", "config")
        self.growth_file = os.path.join(self.config_dir, "erika_growth.md")

    async def evolve(self, latest_reflection: str) -> None:
        """
        Updates the living personality profile ('Growth') based on recent reflections.
        This is the 'Transformation' step of the subconscious cycle.
        """
        logger.info("GrowthService: Initiating personality evolution...")
        
        # 1. Check Offline Status (Safety)
        # We strictly use the Remote Brain for subconscious tasks to avoid blocking the main brain.
        if not self.router.status.get('remote'):
             logger.warning("GrowthService: Remote Brain offline. Skipping evolution.")
             return

        # 2. Load Current State
        current_growth = ""
        if os.path.exists(self.growth_file):
             try:
                 with open(self.growth_file, 'r', encoding='utf-8') as f:
                     current_growth = f.read()
             except Exception as e:
                 logger.error(f"GrowthService: Failed to read existing growth file: {e}")

        # 3. Construct Prompt
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

        # 4. Generate
        remote_host = self.router.REMOTE_BRAIN 
        remote_model = self.router.REMOTE_MODEL
        
        new_growth = ""
        try:
            logger.info("GrowthService: Dreaming of new traits...")
            async for chunk in self.brain.generate_response(
                model=remote_model, 
                messages=[{"role": "user", "content": prompt}], 
                host=remote_host
            ):
                if "message" in chunk:
                    new_growth += chunk['message'].get('content', '')
            
            # 5. Save
            if new_growth:
                 os.makedirs(os.path.dirname(self.growth_file), exist_ok=True)
                 with open(self.growth_file, 'w', encoding='utf-8') as f:
                     f.write(new_growth)
                 logger.info("GrowthService: Personality Evolved.")
                 
        except Exception as e:
            logger.error(f"GrowthService: Evolution failed: {e}")
