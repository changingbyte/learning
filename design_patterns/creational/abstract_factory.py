"""
Abstract Factory Pattern - Backend Implementation

This module demonstrates the Abstract Factory pattern in the context of backend development,
specifically for creating families of related database connections and query builders.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
import pymongo
from sqlalchemy import create_engine, text
from redis import Redis


# 1. USE CASES
"""
Backend Use Cases for Abstract Factory Pattern:

1. Database Access Layer
   - Create consistent families of database connections and query builders
   - Support multiple database types (SQL, NoSQL, Cache)
   - Maintain connection pools and configurations

2. API Client Libraries
   - Create related sets of API clients
   - Handle different API versions
   - Manage authentication and request formatting

3. Data Storage Systems
   - Create storage backends (File, S3, Database)
   - Handle different storage formats
   - Manage access patterns

4. Caching Systems
   - Create cache providers (Redis, Memcached)
   - Handle different serialization formats
   - Manage cache policies

When to Use:
- When you need families of related objects
- When you want to ensure compatibility between components
- When you need to support multiple backends or providers

When Not to Use:
- When you only need a single type of object
- When objects don't form natural families
- When you don't need to enforce compatibility
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Database Factory Usage:
   ```python
   # Create PostgreSQL factory
   db_factory = PostgreSQLFactory()
   connection = db_factory.create_connection()
   query_builder = db_factory.create_query_builder()
   
   # Execute query
   query = query_builder.select("users").where("active = true")
   result = connection.execute(query)
   ```

2. Cache Factory Usage:
   ```python
   # Create Redis factory
   cache_factory = RedisFactory()
   connection = cache_factory.create_connection()
   serializer = cache_factory.create_serializer()
   
   # Store data
   data = {"user": "john"}
   serialized = serializer.serialize(data)
   connection.set("user:1", serialized)
   ```

3. Storage Factory Usage:
   ```python
   # Create S3 factory
   storage_factory = S3StorageFactory()
   client = storage_factory.create_client()
   uploader = storage_factory.create_uploader()
   
   # Upload file
   uploader.upload("data.csv", client)
   ```
"""


# 3. IMPLEMENTATION

# Abstract Product Classes
class DatabaseConnection(ABC):
    """Abstract database connection."""
    
    @abstractmethod
    def connect(self) -> None:
        """Establish connection."""
        pass
    
    @abstractmethod
    def execute(self, query: Any) -> List[Dict[str, Any]]:
        """Execute a query."""
        pass


class QueryBuilder(ABC):
    """Abstract query builder."""
    
    @abstractmethod
    def select(self, table: str) -> 'QueryBuilder':
        """Create SELECT query."""
        pass
    
    @abstractmethod
    def where(self, condition: str) -> 'QueryBuilder':
        """Add WHERE clause."""
        pass
    
    @abstractmethod
    def build(self) -> Any:
        """Build the final query."""
        pass


# Concrete Product Classes for PostgreSQL
class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL specific connection."""
    
    def __init__(self):
        self.engine = None
    
    def connect(self) -> None:
        """Establish PostgreSQL connection."""
        self.engine = create_engine('postgresql://user:pass@localhost:5432/db')
    
    def execute(self, query: Any) -> List[Dict[str, Any]]:
        """Execute SQL query."""
        if not self.engine:
            self.connect()
        with self.engine.connect() as conn:
            result = conn.execute(text(str(query)))
            return [dict(row) for row in result]


class PostgreSQLQueryBuilder(QueryBuilder):
    """PostgreSQL query builder."""
    
    def __init__(self):
        self.query = ""
        self.conditions = []
    
    def select(self, table: str) -> 'QueryBuilder':
        """Create SELECT query."""
        self.query = f"SELECT * FROM {table}"
        return self
    
    def where(self, condition: str) -> 'QueryBuilder':
        """Add WHERE clause."""
        self.conditions.append(condition)
        return self
    
    def build(self) -> str:
        """Build the final query."""
        if self.conditions:
            return f"{self.query} WHERE {' AND '.join(self.conditions)}"
        return self.query


# Concrete Product Classes for MongoDB
class MongoDBConnection(DatabaseConnection):
    """MongoDB specific connection."""
    
    def __init__(self):
        self.client = None
        self.db = None
    
    def connect(self) -> None:
        """Establish MongoDB connection."""
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['mydatabase']
    
    def execute(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute MongoDB query."""
        if not self.db:
            self.connect()
        collection = self.db[query['collection']]
        return list(collection.find(query['filter']))


class MongoDBQueryBuilder(QueryBuilder):
    """MongoDB query builder."""
    
    def __init__(self):
        self.collection = ""
        self.filters = {}
    
    def select(self, collection: str) -> 'QueryBuilder':
        """Set collection to query."""
        self.collection = collection
        return self
    
    def where(self, condition: str) -> 'QueryBuilder':
        """Add filter condition."""
        key, value = condition.split('=')
        self.filters[key.strip()] = value.strip()
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final query."""
        return {
            'collection': self.collection,
            'filter': self.filters
        }


# Abstract Factory
class DatabaseFactory(ABC):
    """Abstract factory for database operations."""
    
    @abstractmethod
    def create_connection(self) -> DatabaseConnection:
        """Create database connection."""
        pass
    
    @abstractmethod
    def create_query_builder(self) -> QueryBuilder:
        """Create query builder."""
        pass


# Concrete Factories
class PostgreSQLFactory(DatabaseFactory):
    """Factory for PostgreSQL database operations."""
    
    def create_connection(self) -> DatabaseConnection:
        """Create PostgreSQL connection."""
        return PostgreSQLConnection()
    
    def create_query_builder(self) -> QueryBuilder:
        """Create PostgreSQL query builder."""
        return PostgreSQLQueryBuilder()


class MongoDBFactory(DatabaseFactory):
    """Factory for MongoDB database operations."""
    
    def create_connection(self) -> DatabaseConnection:
        """Create MongoDB connection."""
        return MongoDBConnection()
    
    def create_query_builder(self) -> QueryBuilder:
        """Create MongoDB query builder."""
        return MongoDBQueryBuilder()


# Usage Example
def main():
    # PostgreSQL example
    postgres_factory = PostgreSQLFactory()
    postgres_conn = postgres_factory.create_connection()
    postgres_builder = postgres_factory.create_query_builder()
    
    try:
        # Build and execute PostgreSQL query
        query = postgres_builder.select("users").where("active = true").build()
        result = postgres_conn.execute(query)
        print("PostgreSQL Result:", result)
    except Exception as e:
        print(f"PostgreSQL Error: {e}")
    
    # MongoDB example
    mongo_factory = MongoDBFactory()
    mongo_conn = mongo_factory.create_connection()
    mongo_builder = mongo_factory.create_query_builder()
    
    try:
        # Build and execute MongoDB query
        query = mongo_builder.select("users").where("active=true").build()
        result = mongo_conn.execute(query)
        print("MongoDB Result:", result)
    except Exception as e:
        print(f"MongoDB Error: {e}")


if __name__ == "__main__":
    main() 