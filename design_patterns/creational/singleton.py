"""
Singleton Pattern - Backend Implementation

This module demonstrates the Singleton pattern in the context of backend development,
specifically for managing shared resources like database connections and configuration.
"""

from typing import Optional
import threading
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
import redis
from redis import Redis


# 1. USE CASES
"""
Backend Use Cases for Singleton Pattern:

1. Database Connection Pools
   - Maintain a single connection pool across the application
   - Prevent resource exhaustion from multiple connection instances
   - Ensure consistent database access configuration

2. Configuration Management
   - Store application settings loaded from config files
   - Maintain environment variables
   - Ensure consistent configuration across all services

3. Cache Management
   - Share Redis connection across services
   - Maintain in-memory cache for frequently accessed data
   - Ensure cache consistency

4. Logging Service
   - Centralize logging configuration
   - Ensure consistent log formatting
   - Prevent multiple file handles to log files

When to Use:
- When exactly one instance of a class is needed globally
- When you need strict control over global state
- When resource sharing must be coordinated from a central point

When Not to Use:
- When you need multiple instances with different configurations
- When the object carries state that should vary between instances
- When you need to scale horizontally with different configurations
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Database Connection Pool:
   ```python
   db = DatabaseConnection.get_instance()
   result = db.execute("SELECT * FROM users")
   
   # Another part of the application
   same_db = DatabaseConnection.get_instance()  # Returns the same instance
   ```

2. Redis Cache Manager:
   ```python
   cache = RedisCacheManager.get_instance()
   cache.set("user:1", user_data)
   
   # Another service
   same_cache = RedisCacheManager.get_instance()
   user = same_cache.get("user:1")  # Accessing same cache
   ```

3. Application Configuration:
   ```python
   config = AppConfig.get_instance()
   db_url = config.get("DATABASE_URL")
   
   # Another module
   same_config = AppConfig.get_instance()
   api_key = same_config.get("API_KEY")  # Same configuration instance
   ```
"""


# 3. IMPLEMENTATION

class DatabaseConnection:
    """
    A thread-safe singleton class for managing database connections.
    """
    _instance: Optional['DatabaseConnection'] = None
    _lock = threading.Lock()
    _engine: Optional[Engine] = None

    def __new__(cls) -> 'DatabaseConnection':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            self._engine = create_engine(
                "postgresql://user:password@localhost:5432/dbname",
                pool_size=5,
                max_overflow=10
            )

    @classmethod
    def get_instance(cls) -> 'DatabaseConnection':
        """Get the singleton instance of DatabaseConnection."""
        if cls._instance is None:
            cls._instance = DatabaseConnection()
        return cls._instance

    def execute(self, query: str) -> list:
        """Execute a SQL query using the connection."""
        with self._engine.connect() as conn:
            result = conn.execute(query)
            return [dict(row) for row in result]


class RedisCacheManager:
    """
    A thread-safe singleton class for managing Redis cache connections.
    """
    _instance: Optional['RedisCacheManager'] = None
    _lock = threading.Lock()
    _client: Optional[Redis] = None

    def __new__(cls) -> 'RedisCacheManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )

    @classmethod
    def get_instance(cls) -> 'RedisCacheManager':
        """Get the singleton instance of RedisCacheManager."""
        if cls._instance is None:
            cls._instance = RedisCacheManager()
        return cls._instance

    def set(self, key: str, value: str, expire: int = None) -> bool:
        """Set a value in Redis cache."""
        return self._client.set(key, value, ex=expire)

    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis cache."""
        return self._client.get(key)


# Usage Example
def main():
    # Database Connection Example
    db1 = DatabaseConnection.get_instance()
    db2 = DatabaseConnection.get_instance()
    assert db1 is db2, "Database connections should be the same instance"

    # Redis Cache Example
    cache1 = RedisCacheManager.get_instance()
    cache2 = RedisCacheManager.get_instance()
    assert cache1 is cache2, "Cache managers should be the same instance"

    # Using the instances
    try:
        # Database operations
        users = db1.execute("SELECT * FROM users LIMIT 5")
        print("Users:", users)

        # Cache operations
        cache1.set("test_key", "test_value", expire=3600)
        value = cache2.get("test_key")
        print("Cached value:", value)

    except Exception as e:
        print(f"Error during demonstration: {e}")


if __name__ == "__main__":
    main() 