"""
Bridge Pattern - Backend Implementation

This module demonstrates the Bridge pattern in the context of backend development,
specifically for creating a flexible database abstraction layer that separates
database operations from their implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
from datetime import datetime


# 1. USE CASES
"""
Backend Use Cases for Bridge Pattern:

1. Database Abstraction
   - Separate database operations from implementations
   - Support multiple database types
   - Handle different query formats

2. Caching Systems
   - Separate cache operations from storage backends
   - Support different cache providers
   - Handle different serialization formats

3. Message Queue Systems
   - Separate queue operations from providers
   - Support different message brokers
   - Handle different message formats

4. File Storage Systems
   - Separate storage operations from providers
   - Support different storage backends
   - Handle different file formats

When to Use:
- When you need to separate an abstraction from its implementation
- When both the abstraction and implementation need to be extended
- When changes in implementation shouldn't affect the client code

When Not to Use:
- When you have a simple system with one implementation
- When there's no need for runtime switching between implementations
- When the abstraction and implementation are tightly coupled
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. Database Operations:
   ```python
   # Create PostgreSQL implementation
   db = Database(PostgreSQLImplementation())
   db.connect()
   db.execute("SELECT * FROM users")
   
   # Switch to MongoDB implementation
   db = Database(MongoDBImplementation())
   db.connect()
   db.execute({"collection": "users"})
   ```

2. Cache Operations:
   ```python
   # Create Redis implementation
   cache = Cache(RedisImplementation())
   cache.set("key", "value")
   
   # Switch to Memcached implementation
   cache = Cache(MemcachedImplementation())
   cache.set("key", "value")
   ```

3. Storage Operations:
   ```python
   # Create S3 implementation
   storage = FileStorage(S3Implementation())
   storage.save("file.txt", data)
   
   # Switch to local filesystem implementation
   storage = FileStorage(LocalFSImplementation())
   storage.save("file.txt", data)
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class QueryResult:
    """Represents a database query result."""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    affected_rows: int = 0
    last_insert_id: Optional[int] = None


class DatabaseImplementation(ABC):
    """Abstract database implementation."""
    
    @abstractmethod
    def connect(self, connection_string: str) -> bool:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Close database connection."""
        pass
    
    @abstractmethod
    def execute_query(self, query: Any) -> QueryResult:
        """Execute a database query."""
        pass
    
    @abstractmethod
    def begin_transaction(self) -> bool:
        """Begin a database transaction."""
        pass
    
    @abstractmethod
    def commit_transaction(self) -> bool:
        """Commit a database transaction."""
        pass
    
    @abstractmethod
    def rollback_transaction(self) -> bool:
        """Rollback a database transaction."""
        pass


class PostgreSQLImplementation(DatabaseImplementation):
    """PostgreSQL specific implementation."""
    
    def __init__(self):
        self.connected = False
        self.in_transaction = False
    
    def connect(self, connection_string: str) -> bool:
        """Connect to PostgreSQL database."""
        # Simulate PostgreSQL connection
        print(f"Connecting to PostgreSQL: {connection_string}")
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from PostgreSQL database."""
        if self.connected:
            print("Disconnecting from PostgreSQL")
            self.connected = False
            return True
        return False
    
    def execute_query(self, query: str) -> QueryResult:
        """Execute SQL query."""
        if not self.connected:
            return QueryResult(success=False, error="Not connected")
        
        try:
            print(f"Executing PostgreSQL query: {query}")
            # Simulate query execution
            if query.lower().startswith("select"):
                data = [
                    {"id": 1, "name": "John"},
                    {"id": 2, "name": "Jane"}
                ]
                return QueryResult(success=True, data=data)
            else:
                return QueryResult(success=True, affected_rows=1, last_insert_id=1)
        
        except Exception as e:
            return QueryResult(success=False, error=str(e))
    
    def begin_transaction(self) -> bool:
        """Begin PostgreSQL transaction."""
        if not self.connected:
            return False
        print("Beginning PostgreSQL transaction")
        self.in_transaction = True
        return True
    
    def commit_transaction(self) -> bool:
        """Commit PostgreSQL transaction."""
        if not self.in_transaction:
            return False
        print("Committing PostgreSQL transaction")
        self.in_transaction = False
        return True
    
    def rollback_transaction(self) -> bool:
        """Rollback PostgreSQL transaction."""
        if not self.in_transaction:
            return False
        print("Rolling back PostgreSQL transaction")
        self.in_transaction = False
        return True


class MongoDBImplementation(DatabaseImplementation):
    """MongoDB specific implementation."""
    
    def __init__(self):
        self.connected = False
        self.in_transaction = False
    
    def connect(self, connection_string: str) -> bool:
        """Connect to MongoDB database."""
        # Simulate MongoDB connection
        print(f"Connecting to MongoDB: {connection_string}")
        self.connected = True
        return True
    
    def disconnect(self) -> bool:
        """Disconnect from MongoDB database."""
        if self.connected:
            print("Disconnecting from MongoDB")
            self.connected = False
            return True
        return False
    
    def execute_query(self, query: Dict[str, Any]) -> QueryResult:
        """Execute MongoDB query."""
        if not self.connected:
            return QueryResult(success=False, error="Not connected")
        
        try:
            print(f"Executing MongoDB query: {json.dumps(query)}")
            # Simulate query execution
            if "find" in query:
                data = [
                    {"_id": 1, "name": "John"},
                    {"_id": 2, "name": "Jane"}
                ]
                return QueryResult(success=True, data=data)
            else:
                return QueryResult(success=True, affected_rows=1)
        
        except Exception as e:
            return QueryResult(success=False, error=str(e))
    
    def begin_transaction(self) -> bool:
        """Begin MongoDB transaction."""
        if not self.connected:
            return False
        print("Beginning MongoDB transaction")
        self.in_transaction = True
        return True
    
    def commit_transaction(self) -> bool:
        """Commit MongoDB transaction."""
        if not self.in_transaction:
            return False
        print("Committing MongoDB transaction")
        self.in_transaction = False
        return True
    
    def rollback_transaction(self) -> bool:
        """Rollback MongoDB transaction."""
        if not self.in_transaction:
            return False
        print("Rolling back MongoDB transaction")
        self.in_transaction = False
        return True


class Database:
    """Database abstraction that uses a bridge to implementation."""
    
    def __init__(self, implementation: DatabaseImplementation):
        self._impl = implementation
        self._connected = False
    
    def connect(self, host: str, port: int, database: str,
               username: str = "", password: str = "") -> bool:
        """Connect to database using implementation."""
        connection_string = self._build_connection_string(
            host, port, database, username, password
        )
        self._connected = self._impl.connect(connection_string)
        return self._connected
    
    def disconnect(self) -> bool:
        """Disconnect from database."""
        if self._connected:
            self._connected = not self._impl.disconnect()
            return not self._connected
        return True
    
    def query(self, query: Any) -> QueryResult:
        """Execute query using implementation."""
        if not self._connected:
            return QueryResult(success=False, error="Not connected to database")
        return self._impl.execute_query(query)
    
    def transaction(self) -> 'DatabaseTransaction':
        """Create a transaction context manager."""
        return DatabaseTransaction(self._impl)
    
    def _build_connection_string(self, host: str, port: int, database: str,
                               username: str, password: str) -> str:
        """Build connection string based on implementation type."""
        if isinstance(self._impl, PostgreSQLImplementation):
            auth = f"{username}:{password}@" if username and password else ""
            return f"postgresql://{auth}{host}:{port}/{database}"
        elif isinstance(self._impl, MongoDBImplementation):
            auth = f"{username}:{password}@" if username and password else ""
            return f"mongodb://{auth}{host}:{port}/{database}"
        else:
            raise ValueError("Unknown database implementation")


class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, implementation: DatabaseImplementation):
        self._impl = implementation
    
    def __enter__(self):
        """Begin transaction."""
        self._impl.begin_transaction()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback transaction."""
        if exc_type is None:
            # No exception occurred, commit the transaction
            self._impl.commit_transaction()
        else:
            # Exception occurred, rollback the transaction
            self._impl.rollback_transaction()
            return False  # Re-raise the exception


# Usage Example
def main():
    # PostgreSQL example
    postgres_db = Database(PostgreSQLImplementation())
    
    try:
        # Connect to database
        postgres_db.connect(
            host="localhost",
            port=5432,
            database="test_db",
            username="user",
            password="pass"
        )
        
        # Execute some queries
        select_result = postgres_db.query(
            "SELECT * FROM users WHERE active = true"
        )
        print("\nPostgreSQL Select Result:", json.dumps(
            select_result.__dict__,
            indent=2,
            default=str
        ))
        
        # Use transaction
        with postgres_db.transaction():
            insert_result = postgres_db.query(
                "INSERT INTO users (name, email) VALUES ('John', 'john@example.com')"
            )
            print("\nPostgreSQL Insert Result:", json.dumps(
                insert_result.__dict__,
                indent=2,
                default=str
            ))
        
        # Disconnect
        postgres_db.disconnect()
    
    except Exception as e:
        print(f"PostgreSQL Error: {e}")
    
    # MongoDB example
    mongo_db = Database(MongoDBImplementation())
    
    try:
        # Connect to database
        mongo_db.connect(
            host="localhost",
            port=27017,
            database="test_db"
        )
        
        # Execute some queries
        find_result = mongo_db.query({
            "find": "users",
            "filter": {"active": True}
        })
        print("\nMongoDB Find Result:", json.dumps(
            find_result.__dict__,
            indent=2,
            default=str
        ))
        
        # Use transaction
        with mongo_db.transaction():
            insert_result = mongo_db.query({
                "insert": "users",
                "documents": [{
                    "name": "John",
                    "email": "john@example.com"
                }]
            })
            print("\nMongoDB Insert Result:", json.dumps(
                insert_result.__dict__,
                indent=2,
                default=str
            ))
        
        # Disconnect
        mongo_db.disconnect()
    
    except Exception as e:
        print(f"MongoDB Error: {e}")


if __name__ == "__main__":
    main() 