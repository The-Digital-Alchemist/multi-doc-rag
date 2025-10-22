from typing import List, Dict


class ConversationMemory:
    """Manages conversation memory for a single session."""
    
    MAX_MEMORY = 3

    def __init__(self, session_id: str):
        """Initialize conversation memory for a session."""
        self.session_id = session_id
        self.memory: List[Dict] = []


    def get_memory(self) -> List[Dict]:
        """Get recent conversation memory for this session."""
        # Return the list of Q/A pairs for this session
        return self.memory

    


    def add_message(self, message: str, response: str) -> List[Dict]:
        """Add a Q/A pair to memory, maintaining the limit."""
        # Remove oldest conversation when memory is full
        if len(self.memory) >= self.MAX_MEMORY:
            self.memory.pop(0)
        
        # Store Q/A pair with consistent field names
        self.memory.append({
            "query": message,    
            "response": response 
        })
        return self.memory

    
    def clear_memory(self) -> List[Dict]:
        """Clear all memory for this session."""
        # Reset memory to empty list
        self.memory = []
        return self.memory

