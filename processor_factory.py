from i_process_frame import IProcessFrame
from process_frame_openai import ProcessFrameOpenAI
from process_frame_mistral import ProcessFrameMistral
from exceptions import ProcessorNotFoundError
from config import config

class ProcessorFactory:
    """Factory for creating frame processor instances."""
    
    _processors = {
        'openai': ProcessFrameOpenAI,
        'mistral': ProcessFrameMistral
    }
    
    @classmethod
    def create_processor(cls, implementation: str) -> IProcessFrame:
        """Create a processor instance based on the implementation name."""
        if implementation not in cls._processors:
            raise ProcessorNotFoundError(
                f"Invalid implementation specified: {implementation}",
                f"Available implementations: {list(cls._processors.keys())}"
            )
        
        # Initialize the processor with configuration
        if implementation == 'openai':
            return ProcessFrameOpenAI(config.OPENAI_API_KEY, config.OPENAI_MODEL)
        elif implementation == 'mistral':
            return ProcessFrameMistral(config.MISTRAL_API_KEY, config.MISTRAL_MODEL)
        
        # Fallback to default instantiation
        return cls._processors[implementation]()
    
    @classmethod
    def register_processor(cls, name: str, processor_class):
        """Register a new processor implementation."""
        cls._processors[name] = processor_class
    
    @classmethod
    def get_available_processors(cls):
        """Get list of available processor implementations."""
        return list(cls._processors.keys())