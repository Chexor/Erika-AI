import os
import datetime
import logging
from typing import List, Optional, Callable

logger = logging.getLogger(__name__)

class SafeTools:
    """
    The 'Action Space' exposed to the Recursive Brain.
    All methods here are accessible via the `tools` object in the REPL.
    """
    def __init__(self, context_root: str, delegate_callback: Optional[Callable] = None):
        """
        Args:
            context_root: The root directory where files can be read (Erika's workspace).
            delegate_callback: A function `fn(prompt, context) -> str` to call for recursion.
        """
        self.context_root = os.path.abspath(context_root)
        self.delegate_callback = delegate_callback

    def _is_safe_path(self, path: str) -> bool:
        """Ensures path is within context_root."""
        if os.path.isabs(path):
            return False
        abs_path = os.path.abspath(os.path.join(self.context_root, path))
        try:
            return os.path.commonpath([self.context_root, abs_path]) == self.context_root
        except ValueError:
            return False

    def get_time(self) -> str:
        """Returns the current server time."""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def list_dir(self, path: str = ".") -> str:
        """Lists files in a directory (non-recursive)."""
        if not self._is_safe_path(path):
            return "Error: Access Denied (Path outside workspace)"
        
        target_path = os.path.join(self.context_root, path)
        if not os.path.exists(target_path):
            return "Error: Directory not found"
        
        try:
            items = os.listdir(target_path)
            # Filter out hidden files/dirs
            items = [i for i in items if not i.startswith('.')]
            return str(items[:50]) # Limit to 50 items
        except Exception as e:
            return f"Error: {e}"

    def read_file(self, path: str, lines: Optional[str] = None) -> str:
        """
        Reads a text file.
        Args:
            path: Relative path to the file.
            lines: Optional range "1-50" (1-based).
        """
        if not self._is_safe_path(path):
            return "Error: Access Denied (Path outside workspace)"

        target_path = os.path.join(self.context_root, path)
        if not os.path.isfile(target_path):
            return f"Error: File not found: {path}"

        try:
            with open(target_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
            
            if not all_lines:
                return "[Empty File]"

            start, end = 0, len(all_lines)
            if lines:
                try:
                    parts = lines.split('-')
                    if len(parts) == 2:
                        # Convert 1-based "1-50" to 0-based slice
                        s_user = int(parts[0])
                        e_user = int(parts[1])
                        start = max(0, s_user - 1)
                        end = min(len(all_lines), e_user)
                except ValueError:
                    return "Error: Invalid line format. Use '1-50'."

            # Safety cap
            if (end - start) > 500:
                end = start + 500
                return "".join(all_lines[start:end]) + "\n... [Truncated at 500 lines]"
            
            return "".join(all_lines[start:end])

        except Exception as e:
            return f"Error reading file: {e}"

    def search_memory(self, query: str) -> str:
        """
        Phase 1: Simple Keyword Search.
        Searches .txt and .md files in workspace for the query string.
        """
        # TODO: This is a naive implementation. 
        # In a real scenario, this should query the Memory module.
        # For Phase 1, we will implement a basic grep.
        
        results = []
        MAX_RESULTS = 5
        
        # Walk the directory
        count = 0
        for root, dirs, files in os.walk(self.context_root):
             # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.endswith(('.md', '.txt', '.py', '.json')):
                    filepath = os.path.join(root, file)
                    relpath = os.path.relpath(filepath, self.context_root)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                results.append(f"Found in {relpath}")
                                count += 1
                                if count >= MAX_RESULTS:
                                    break
                    except:
                        continue
            if count >= MAX_RESULTS:
                break
        
        if not results:
            return "No matches found."
        
        return "\n".join(results)

    def delegate_thought(self, prompt: str, context: str) -> str:
        """
        The Recursive Primitive.
        Spawns a sub-agent (Gemma 2) to process the context with the prompt.
        """
        if not self.delegate_callback:
            return "Error: Recursion not enabled (No callback provided)"
        
        logger.info(f"SafeTools: Delegating thought '{prompt[:30]}...'")
        try:
            # Check length safety
            if len(context) > 100000:
                return "Error: Context too large for recursion (Max 100k chars)"
                
            return self.delegate_callback(prompt, context)
        except Exception as e:
            logger.error(f"Recursion failed: {e}")
            return f"Error during recursion: {e}"
