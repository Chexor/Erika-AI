
import os
import json
import datetime
import logging

logger = logging.getLogger("domain.subconscious.growth")

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
        
        # 1. Determine Brain (Lucid Dreaming Upgrade)
        remote_online = self.router.status.get('remote')
        target_host = self.router.REMOTE_BRAIN if remote_online else self.router.LOCAL_BRAIN
        target_model = self.router.REMOTE_MODEL if remote_online else self.router.LOCAL_MODEL

        logger.info(f"GrowthService: Evolving via {'Remote' if remote_online else 'Local (Erika Core)'} [{target_model}]")

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
        new_growth = ""
        try:
            logger.info("GrowthService: Dreaming of new traits...")
            async for chunk in self.brain.generate_response(
                model=target_model, 
                messages=[{"role": "user", "content": prompt}], 
                host=target_host
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
