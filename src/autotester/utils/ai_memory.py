import json
import os
import threading

class AIMemory:
    """
    A thread-safe class to manage the AI's memory of successful selectors.
    This helps the AI learn and become faster over time.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, filepath='ai_memory.json'):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(AIMemory, cls).__new__(cls)
                cls._instance.filepath = filepath
                cls._instance.memory = cls._instance._load()
        return cls._instance

    def _load(self):
        """Loads memory from the JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self):
        """Saves the current memory to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def remember(self, page_url, element_name, selector):
        """Remembers a successful selector for a given page and element."""
        with self._lock:
            key = f"{page_url}::{element_name}"
            self.memory[key] = selector
            self._save()

    def recall(self, page_url, element_name):
        """Recalls a selector from memory."""
        key = f"{page_url}::{element_name}"
        return self.memory.get(key)

# Initialize a singleton instance
memory_singleton = AIMemory()