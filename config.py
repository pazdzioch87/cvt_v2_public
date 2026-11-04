import os
from typing import Optional

class Config:
    """Configuration management for the CVT application."""
    
    def __init__(self):
        # API Keys
        self.OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
        self.MISTRAL_API_KEY: Optional[str] = os.getenv('MISTRAL_API_KEY')
        
        # Environment settings
        self.PYTHON_ENV: str = os.getenv('PYTHON_ENV', 'development')
        self.YOLO_VERBOSE: bool = os.getenv('YOLO_VERBOSE', 'False').lower() == 'true'
        
        # Model settings
        self.YOLO_MODEL_PATH: str = os.getenv('YOLO_MODEL_PATH', 'yolo11n.pt')
        self.OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.MISTRAL_MODEL: str = os.getenv('MISTRAL_MODEL', 'pixtral-12b-2409')
        
        # Server settings
        self.HOST: str = os.getenv('HOST', '127.0.0.1')
        self.PORT: int = int(os.getenv('PORT', '8000'))
        
        # SRS settings
        self.SRS_HOST: str = os.getenv('SRS_HOST', 'srs')
        
    @property
    def is_development(self) -> bool:
        return self.PYTHON_ENV == 'development'
        
    @property
    def is_production(self) -> bool:
        return self.PYTHON_ENV == 'production'

# Global configuration instance
config = Config()