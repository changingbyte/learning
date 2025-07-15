"""
Prototype Pattern - Backend Implementation

This module demonstrates the Prototype pattern in the context of backend development,
specifically for managing configuration templates and service configurations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import copy
import json
from dataclasses import dataclass, field
from datetime import timedelta


# 1. USE CASES
"""
Backend Use Cases for Prototype Pattern:

1. Service Configuration Templates
   - Create base configurations for different services
   - Customize configurations for different environments
   - Clone and modify service settings

2. Database Connection Pools
   - Create template connection configurations
   - Clone and customize for different databases
   - Manage connection settings for different environments

3. API Client Settings
   - Define template API client configurations
   - Clone and customize for different API endpoints
   - Manage different authentication settings

4. Cache Configuration
   - Create template cache settings
   - Clone and modify for different cache types
   - Customize TTL and storage options

When to Use:
- When creating objects is more expensive than cloning
- When you need many instances with similar configurations
- When you want to avoid a hierarchy of factory classes

When Not to Use:
- When object creation is simple
- When objects have unique states that can't be shared
- When deep copying would be too complex or expensive
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Service Configuration:
   ```python
   base_config = ServiceConfig(name="api-service", port=8080)
   dev_config = base_config.clone()
   dev_config.set_environment("development")
   
   prod_config = base_config.clone()
   prod_config.set_environment("production")
   ```

2. Database Configuration:
   ```python
   base_db = DatabaseConfig(driver="postgresql")
   test_db = base_db.clone()
   test_db.set_credentials("test_user", "test_pass")
   
   prod_db = base_db.clone()
   prod_db.set_credentials("prod_user", "prod_pass")
   ```

3. Cache Configuration:
   ```python
   base_cache = CacheConfig(provider="redis")
   short_cache = base_cache.clone()
   short_cache.set_ttl(minutes=5)
   
   long_cache = base_cache.clone()
   long_cache.set_ttl(hours=24)
   ```
"""


# 3. IMPLEMENTATION

class Prototype(ABC):
    """Abstract prototype interface."""
    
    @abstractmethod
    def clone(self) -> 'Prototype':
        """Create a deep copy of the current object."""
        pass


@dataclass
class DatabaseSettings:
    """Database connection settings."""
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database: str = ""
    max_connections: int = 10
    timeout: int = 30


@dataclass
class CacheSettings:
    """Cache configuration settings."""
    provider: str = "redis"
    host: str = "localhost"
    port: int = 6379
    ttl: int = 3600  # seconds
    max_entries: int = 1000


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    output: str = "console"
    file_path: Optional[str] = None


class ServiceConfig(Prototype):
    """Service configuration prototype."""
    
    def __init__(
        self,
        name: str,
        environment: str = "development",
        version: str = "1.0.0",
        port: int = 8080,
        debug: bool = False
    ):
        self.name = name
        self.environment = environment
        self.version = version
        self.port = port
        self.debug = debug
        self.database = DatabaseSettings()
        self.cache = CacheSettings()
        self.logging = LoggingSettings()
        self._custom_settings: Dict[str, Any] = {}
    
    def clone(self) -> 'ServiceConfig':
        """Create a deep copy of the service configuration."""
        return copy.deepcopy(self)
    
    def set_environment(self, environment: str) -> None:
        """Set the environment and adjust settings accordingly."""
        self.environment = environment
        if environment == "production":
            self.debug = False
            self.logging.level = "WARNING"
        elif environment == "development":
            self.debug = True
            self.logging.level = "DEBUG"
    
    def configure_database(self, **settings) -> None:
        """Configure database settings."""
        for key, value in settings.items():
            if hasattr(self.database, key):
                setattr(self.database, key, value)
    
    def configure_cache(self, **settings) -> None:
        """Configure cache settings."""
        for key, value in settings.items():
            if hasattr(self.cache, key):
                setattr(self.cache, key, value)
    
    def configure_logging(self, **settings) -> None:
        """Configure logging settings."""
        for key, value in settings.items():
            if hasattr(self.logging, key):
                setattr(self.logging, key, value)
    
    def add_custom_setting(self, key: str, value: Any) -> None:
        """Add a custom configuration setting."""
        self._custom_settings[key] = value
    
    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """Get a custom configuration setting."""
        return self._custom_settings.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "name": self.name,
            "environment": self.environment,
            "version": self.version,
            "port": self.port,
            "debug": self.debug,
            "database": self.database.__dict__,
            "cache": self.cache.__dict__,
            "logging": self.logging.__dict__,
            "custom_settings": self._custom_settings
        }


class ConfigurationManager:
    """Manages service configuration templates."""
    
    def __init__(self):
        self._templates: Dict[str, ServiceConfig] = {}
    
    def register_template(self, name: str, config: ServiceConfig) -> None:
        """Register a configuration template."""
        self._templates[name] = config
    
    def get_template(self, name: str) -> Optional[ServiceConfig]:
        """Get a configuration template by name."""
        return self._templates.get(name)
    
    def create_config(self, template_name: str) -> Optional[ServiceConfig]:
        """Create a new configuration from a template."""
        template = self.get_template(template_name)
        if template:
            return template.clone()
        return None


# Usage Example
def main():
    # Create base configuration templates
    api_base = ServiceConfig(
        name="api-service",
        version="1.0.0",
        port=8080
    )
    
    worker_base = ServiceConfig(
        name="worker-service",
        version="1.0.0",
        port=9090
    )
    
    # Configure templates
    api_base.configure_database(
        max_connections=20,
        timeout=60
    )
    api_base.configure_cache(
        ttl=1800,
        max_entries=5000
    )
    
    worker_base.configure_database(
        max_connections=5,
        timeout=120
    )
    worker_base.configure_cache(
        ttl=3600,
        max_entries=1000
    )
    
    # Register templates
    config_manager = ConfigurationManager()
    config_manager.register_template("api", api_base)
    config_manager.register_template("worker", worker_base)
    
    # Create configurations for different environments
    try:
        # API Service Configurations
        api_dev = config_manager.create_config("api")
        if api_dev:
            api_dev.set_environment("development")
            api_dev.configure_database(
                host="localhost",
                database="api_dev"
            )
            print("API Dev Config:", json.dumps(api_dev.to_dict(), indent=2))
        
        api_prod = config_manager.create_config("api")
        if api_prod:
            api_prod.set_environment("production")
            api_prod.configure_database(
                host="db.production",
                database="api_prod"
            )
            print("\nAPI Prod Config:", json.dumps(api_prod.to_dict(), indent=2))
        
        # Worker Service Configurations
        worker_dev = config_manager.create_config("worker")
        if worker_dev:
            worker_dev.set_environment("development")
            worker_dev.add_custom_setting("queue_size", 100)
            print("\nWorker Dev Config:", json.dumps(worker_dev.to_dict(), indent=2))
        
        worker_prod = config_manager.create_config("worker")
        if worker_prod:
            worker_prod.set_environment("production")
            worker_prod.add_custom_setting("queue_size", 1000)
            print("\nWorker Prod Config:", json.dumps(worker_prod.to_dict(), indent=2))
    
    except Exception as e:
        print(f"Error during demonstration: {e}")


if __name__ == "__main__":
    main() 