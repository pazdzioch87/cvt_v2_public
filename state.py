import threading
from typing import Dict, Any, Optional
import multiprocessing

class ThreadSafeState:
    """Thread-safe state management for the CVT application."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {}
        
    def set(self, key: str, value: Any):
        """Set a value in the state."""
        with self._lock:
            self._data[key] = value
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state."""
        with self._lock:
            return self._data.get(key, default)
            
    def delete(self, key: str) -> bool:
        """Delete a key from the state. Returns True if key existed."""
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False
            
    def has(self, key: str) -> bool:
        """Check if a key exists in the state."""
        with self._lock:
            return key in self._data

class ProcessManager:
    """Manager for video analysis processes."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._processes: Dict[str, multiprocessing.Process] = {}
        
    def add_process(self, identifier: str, process: multiprocessing.Process) -> bool:
        """Add a process to management. Returns True if added, False if identifier already exists."""
        with self._lock:
            if identifier in self._processes:
                return False
            self._processes[identifier] = process
            return True
            
    def remove_process(self, identifier: str) -> bool:
        """Remove and terminate a process. Returns True if removed, False if not found."""
        with self._lock:
            if identifier not in self._processes:
                return False
                
            process = self._processes[identifier]
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)  # Wait up to 5 seconds
                
            del self._processes[identifier]
            return True
            
    def get_process(self, identifier: str) -> Optional[multiprocessing.Process]:
        """Get a process by identifier."""
        with self._lock:
            return self._processes.get(identifier)
            
    def has_process(self, identifier: str) -> bool:
        """Check if a process exists."""
        with self._lock:
            return identifier in self._processes
            
    def list_processes(self) -> Dict[str, multiprocessing.Process]:
        """Get a copy of all processes."""
        with self._lock:
            return self._processes.copy()
            
    def stop_all_processes(self):
        """Stop all managed processes."""
        with self._lock:
            identifiers = list(self._processes.keys())
            for identifier in identifiers:
                self.remove_process(identifier)

# Global state instances
app_state = ThreadSafeState()
process_manager = ProcessManager()