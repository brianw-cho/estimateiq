"""
EstimateIQ Configuration Settings

Centralized configuration management.
All settings can be overridden via environment variables.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class Settings:
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "EstimateIQ"
    app_version: str = "0.1.0"
    debug: bool = True
    
    # API
    api_prefix: str = "/api"
    
    # CORS - defaults plus any from CORS_ORIGINS env var
    cors_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:3000", 
        "http://127.0.0.1:3000"
    ])
    
    # Paths (relative to backend directory)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    work_orders_file: str = "work_orders.json"
    parts_catalog_file: str = "parts_catalog.json"
    labor_rates_file: str = "labor_rates.json"
    
    # Vector Store (Phase 2)
    chroma_persist_dir: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # LLM (Future - currently using mock)
    use_real_llm: bool = False
    anthropic_api_key: Optional[str] = None
    
    # Default labor rate
    default_labor_rate: float = 125.00
    
    def __post_init__(self):
        """Load settings from environment variables if present"""
        self.debug = os.getenv("DEBUG", "true").lower() == "true"
        self.use_real_llm = os.getenv("USE_REAL_LLM", "false").lower() == "true"
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Parse CORS origins from environment (comma-separated)
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            self.cors_origins = [origin.strip() for origin in cors_env.split(",")]


# Global settings instance
settings = Settings()
