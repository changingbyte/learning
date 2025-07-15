"""
Flyweight Pattern - Backend Implementation

This module demonstrates the Flyweight pattern in the context of backend development,
specifically for efficient sharing of common data across multiple objects and
optimizing memory usage in data-intensive applications.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import time
from datetime import datetime, timedelta


# 1. USE CASES
"""
Backend Use Cases for Flyweight Pattern:

1. Configuration Management
   - Share common configuration settings
   - Cache environment-specific settings
   - Manage feature flags

2. Data Caching
   - Cache frequently accessed data
   - Share immutable data
   - Optimize memory usage

3. Connection Pooling
   - Share database connections
   - Manage connection settings
   - Optimize resource usage

4. Template Management
   - Share document templates
   - Cache email templates
   - Manage response formats

When to Use:
- When you need to support large numbers of similar objects
- When memory usage is a concern
- When object state can be made external

When Not to Use:
- When object sharing adds more complexity than benefit
- When objects are unique and can't share state
- When performance isn't a concern
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Configuration Management:
   ```python
   config = ConfigurationFlyweight.get_instance("production")
   db_settings = config.get_database_settings()
   cache_settings = config.get_cache_settings()
   ```

2. Connection Pool:
   ```python
   pool = ConnectionPool.get_instance()
   connection1 = pool.get_connection("db1")
   connection2 = pool.get_connection("db1")  # Returns same connection
   ```

3. Template System:
   ```python
   template = TemplateFlyweight.get_instance()
   email = template.get_email_template("welcome")
   response = template.get_response_template("error")
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 10
    timeout: int = 30


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    host: str
    port: int
    database: int
    timeout: int = 300
    max_connections: int = 10


@dataclass
class EmailTemplate:
    """Email template configuration."""
    subject: str
    body: str
    sender: str
    reply_to: Optional[str] = None
    format: str = "html"


class ConfigurationFlyweight:
    """Flyweight factory for configuration management."""
    
    _instances: Dict[str, 'ConfigurationFlyweight'] = {}
    _configs: Dict[str, Dict[str, Any]] = {
        "development": {
            "database": DatabaseConfig(
                host="localhost",
                port=5432,
                database="dev_db",
                username="dev_user",
                password="dev_pass"
            ),
            "cache": CacheConfig(
                host="localhost",
                port=6379,
                database=0
            )
        },
        "production": {
            "database": DatabaseConfig(
                host="prod.db.server",
                port=5432,
                database="prod_db",
                username="prod_user",
                password="prod_pass",
                pool_size=20
            ),
            "cache": CacheConfig(
                host="prod.cache.server",
                port=6379,
                database=0,
                max_connections=50
            )
        }
    }
    
    def __init__(self, environment: str):
        self.environment = environment
        self.config = self._configs.get(environment, {})
    
    @classmethod
    def get_instance(cls, environment: str) -> 'ConfigurationFlyweight':
        """Get or create configuration instance for environment."""
        if environment not in cls._instances:
            cls._instances[environment] = cls(environment)
        return cls._instances[environment]
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self.config["database"]
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return self.config["cache"]


class TemplateFlyweight:
    """Flyweight factory for template management."""
    
    _instance: Optional['TemplateFlyweight'] = None
    _templates: Dict[str, EmailTemplate] = {
        "welcome": EmailTemplate(
            subject="Welcome to Our Service",
            body="Dear {name},\n\nWelcome to our service...",
            sender="noreply@example.com"
        ),
        "password_reset": EmailTemplate(
            subject="Password Reset Request",
            body="Dear {name},\n\nYou requested a password reset...",
            sender="security@example.com"
        ),
        "order_confirmation": EmailTemplate(
            subject="Order Confirmation #{order_id}",
            body="Dear {name},\n\nYour order has been confirmed...",
            sender="orders@example.com"
        )
    }
    
    def __new__(cls) -> 'TemplateFlyweight':
        """Ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'TemplateFlyweight':
        """Get template manager instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_template(self, template_name: str) -> EmailTemplate:
        """Get email template by name."""
        if template_name not in self._templates:
            raise ValueError(f"Template '{template_name}' not found")
        return self._templates[template_name]
    
    def register_template(self, name: str, template: EmailTemplate) -> None:
        """Register a new template."""
        self._templates[name] = template


class ConnectionPool:
    """Flyweight factory for database connections."""
    
    _instance: Optional['ConnectionPool'] = None
    _connections: Dict[str, List[Dict[str, Any]]] = {}
    
    def __new__(cls) -> 'ConnectionPool':
        """Ensure single instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize connection pool."""
        self._max_connections = 10
        self._connection_timeout = 300  # seconds
    
    @classmethod
    def get_instance(cls) -> 'ConnectionPool':
        """Get connection pool instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_connection(self, database: str) -> Dict[str, Any]:
        """Get a connection from the pool."""
        # Initialize pool for database if not exists
        if database not in self._connections:
            self._connections[database] = []
        
        # Clean expired connections
        self._clean_expired_connections(database)
        
        # Find available connection
        for conn in self._connections[database]:
            if not conn["in_use"]:
                conn["in_use"] = True
                conn["last_used"] = datetime.now()
                return conn
        
        # Create new connection if pool not full
        if len(self._connections[database]) < self._max_connections:
            connection = self._create_connection(database)
            self._connections[database].append(connection)
            return connection
        
        raise Exception("Connection pool exhausted")
    
    def release_connection(self, database: str, connection: Dict[str, Any]) -> None:
        """Release connection back to pool."""
        if database in self._connections:
            for conn in self._connections[database]:
                if conn["id"] == connection["id"]:
                    conn["in_use"] = False
                    conn["last_used"] = datetime.now()
                    break
    
    def _create_connection(self, database: str) -> Dict[str, Any]:
        """Create a new database connection."""
        # Simulate connection creation
        connection = {
            "id": f"conn_{database}_{len(self._connections[database])}",
            "database": database,
            "created_at": datetime.now(),
            "last_used": datetime.now(),
            "in_use": True
        }
        return connection
    
    def _clean_expired_connections(self, database: str) -> None:
        """Remove expired connections."""
        if database in self._connections:
            now = datetime.now()
            self._connections[database] = [
                conn for conn in self._connections[database]
                if (now - conn["last_used"]).seconds < self._connection_timeout
            ]


# Usage Example
def main():
    try:
        # Configuration Management Example
        print("Configuration Management Example:")
        dev_config = ConfigurationFlyweight.get_instance("development")
        prod_config = ConfigurationFlyweight.get_instance("production")
        
        print("\nDevelopment Database Config:")
        print(json.dumps(dev_config.get_database_config().__dict__, indent=2))
        
        print("\nProduction Cache Config:")
        print(json.dumps(prod_config.get_cache_config().__dict__, indent=2))
        
        # Template Management Example
        print("\nTemplate Management Example:")
        template_manager = TemplateFlyweight.get_instance()
        
        welcome_template = template_manager.get_template("welcome")
        print("\nWelcome Template:")
        print(json.dumps(welcome_template.__dict__, indent=2))
        
        # Register new template
        new_template = EmailTemplate(
            subject="Newsletter #{issue}",
            body="Dear {name},\n\nHere's your newsletter...",
            sender="newsletter@example.com"
        )
        template_manager.register_template("newsletter", new_template)
        
        # Connection Pool Example
        print("\nConnection Pool Example:")
        pool = ConnectionPool.get_instance()
        
        # Get connections
        conn1 = pool.get_connection("users_db")
        print("\nConnection 1:", json.dumps(conn1, indent=2, default=str))
        
        conn2 = pool.get_connection("users_db")
        print("\nConnection 2:", json.dumps(conn2, indent=2, default=str))
        
        # Release connection
        pool.release_connection("users_db", conn1)
        print("\nReleased Connection 1")
        
        # Get another connection (should reuse released connection)
        conn3 = pool.get_connection("users_db")
        print("\nConnection 3 (reused):", json.dumps(conn3, indent=2, default=str))
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 