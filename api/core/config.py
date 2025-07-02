"""
Configuration management for the Bitcoin Balance Tracker API
"""

import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Basic API Configuration
    api_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = False
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API Key Authentication (simplified)
    api_key: str = "your-api-key-change-in-production"
    
    # SSL Configuration
    ssl_cert_path: Optional[str] = None
    ssl_key_path: Optional[str] = None
    
    # CORS Configuration (your website only)
    cors_origins: str = "http://localhost:3000,http://localhost:8080,https://yourwebsite.com"
    
    # Rate Limiting Configuration
    rate_limit_requests_per_minute: int = 120
    rate_limit_burst: int = 20
    
    # IP Allow List (optional - your server IPs)
    allowed_ips: str = ""
    
    # Bitcoin Tracker Configuration
    bitcoin_config_path: str = "config.json"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # API Key Configuration
    api_key_header_name: str = "X-API-Key"
    
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v):
        if v not in ['development', 'staging', 'production']:
            raise ValueError('Environment must be development, staging, or production')
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from string to list"""
        if not self.cors_origins:
            return []
        return [i.strip() for i in self.cors_origins.split(",") if i.strip()]
    
    @property
    def allowed_ips_list(self) -> List[str]:
        """Parse allowed IPs from string to list"""
        if not self.allowed_ips:
            return []
        return [i.strip() for i in self.allowed_ips.split(",") if i.strip()]
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


def get_production_settings() -> Settings:
    """Production environment settings"""
    settings = get_settings()
    settings.debug = False
    settings.log_level = "INFO"
    
    # Require API key in production
    if not os.getenv("API_KEY"):
        raise ValueError("API_KEY environment variable required for production")
    
    return settings 