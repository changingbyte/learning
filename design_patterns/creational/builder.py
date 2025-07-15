"""
Builder Pattern - Backend Implementation

This module demonstrates the Builder pattern in the context of backend development,
specifically for constructing complex API responses with nested data structures.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


# 1. USE CASES
"""
Backend Use Cases for Builder Pattern:

1. API Response Construction
   - Build complex JSON responses with nested structures
   - Include metadata, pagination, and related resources
   - Handle different response formats and versions

2. Query Construction
   - Build complex database queries
   - Handle multiple conditions and joins
   - Support different query formats

3. Configuration Objects
   - Build complex configuration objects
   - Handle dependencies between settings
   - Support different environments

4. Report Generation
   - Build complex reports with multiple sections
   - Handle different output formats
   - Include various data aggregations

When to Use:
- When you need to create complex objects step by step
- When object construction needs to be independent of the parts
- When you need fine control over the construction process

When Not to Use:
- When object construction is simple
- When you don't need different representations
- When you don't need to control the construction process
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. API Response Builder:
   ```python
   response = (APIResponseBuilder()
              .set_status(200)
              .set_data(user_data)
              .add_metadata({"version": "1.0"})
              .add_pagination(total=100, page=1)
              .build())
   ```

2. Query Builder:
   ```python
   query = (QueryBuilder()
           .select("users")
           .where("status = 'active'")
           .order_by("created_at", "DESC")
           .limit(10)
           .build())
   ```

3. Report Builder:
   ```python
   report = (ReportBuilder()
            .add_header("Sales Report")
            .add_summary(summary_data)
            .add_details(details_data)
            .add_footer("Generated on 2024-01-01")
            .build())
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class APIResponse:
    """Represents a complete API response."""
    status: int
    data: Any
    message: str
    metadata: Dict[str, Any]
    pagination: Optional[Dict[str, int]] = None
    errors: Optional[List[Dict[str, str]]] = None
    links: Optional[Dict[str, str]] = None
    included: Optional[List[Dict[str, Any]]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        response_dict = {
            "status": self.status,
            "data": self.data,
            "message": self.message,
            "metadata": self.metadata
        }
        
        if self.pagination:
            response_dict["pagination"] = self.pagination
        if self.errors:
            response_dict["errors"] = self.errors
        if self.links:
            response_dict["links"] = self.links
        if self.included:
            response_dict["included"] = self.included
        
        return response_dict


class ResponseBuilder(ABC):
    """Abstract builder for API responses."""
    
    @abstractmethod
    def set_status(self, status: int) -> 'ResponseBuilder':
        """Set response status."""
        pass
    
    @abstractmethod
    def set_data(self, data: Any) -> 'ResponseBuilder':
        """Set response data."""
        pass
    
    @abstractmethod
    def set_message(self, message: str) -> 'ResponseBuilder':
        """Set response message."""
        pass
    
    @abstractmethod
    def add_metadata(self, metadata: Dict[str, Any]) -> 'ResponseBuilder':
        """Add metadata to response."""
        pass
    
    @abstractmethod
    def add_pagination(self, total: int, page: int, per_page: int = 10) -> 'ResponseBuilder':
        """Add pagination information."""
        pass
    
    @abstractmethod
    def add_error(self, code: str, detail: str) -> 'ResponseBuilder':
        """Add error information."""
        pass
    
    @abstractmethod
    def add_links(self, links: Dict[str, str]) -> 'ResponseBuilder':
        """Add HATEOAS links."""
        pass
    
    @abstractmethod
    def add_included(self, included: List[Dict[str, Any]]) -> 'ResponseBuilder':
        """Add included resources."""
        pass
    
    @abstractmethod
    def build(self) -> APIResponse:
        """Build the final response."""
        pass


class APIResponseBuilder(ResponseBuilder):
    """Concrete builder for API responses."""
    
    def __init__(self):
        self.reset()
    
    def reset(self) -> None:
        """Reset the builder to initial state."""
        self._status = 200
        self._data = None
        self._message = ""
        self._metadata = {"timestamp": datetime.utcnow().isoformat()}
        self._pagination = None
        self._errors = None
        self._links = None
        self._included = None
    
    def set_status(self, status: int) -> 'ResponseBuilder':
        """Set response status."""
        self._status = status
        return self
    
    def set_data(self, data: Any) -> 'ResponseBuilder':
        """Set response data."""
        self._data = data
        return self
    
    def set_message(self, message: str) -> 'ResponseBuilder':
        """Set response message."""
        self._message = message
        return self
    
    def add_metadata(self, metadata: Dict[str, Any]) -> 'ResponseBuilder':
        """Add metadata to response."""
        self._metadata.update(metadata)
        return self
    
    def add_pagination(self, total: int, page: int, per_page: int = 10) -> 'ResponseBuilder':
        """Add pagination information."""
        total_pages = (total + per_page - 1) // per_page
        self._pagination = {
            "total": total,
            "per_page": per_page,
            "current_page": page,
            "total_pages": total_pages
        }
        return self
    
    def add_error(self, code: str, detail: str) -> 'ResponseBuilder':
        """Add error information."""
        if self._errors is None:
            self._errors = []
        self._errors.append({"code": code, "detail": detail})
        return self
    
    def add_links(self, links: Dict[str, str]) -> 'ResponseBuilder':
        """Add HATEOAS links."""
        if self._links is None:
            self._links = {}
        self._links.update(links)
        return self
    
    def add_included(self, included: List[Dict[str, Any]]) -> 'ResponseBuilder':
        """Add included resources."""
        if self._included is None:
            self._included = []
        self._included.extend(included)
        return self
    
    def build(self) -> APIResponse:
        """Build the final response."""
        response = APIResponse(
            status=self._status,
            data=self._data,
            message=self._message,
            metadata=self._metadata,
            pagination=self._pagination,
            errors=self._errors,
            links=self._links,
            included=self._included
        )
        self.reset()
        return response


class ResponseDirector:
    """Director that defines the order of building steps."""
    
    def __init__(self, builder: ResponseBuilder):
        self._builder = builder
    
    def create_success_response(self, data: Any, message: str = "Success") -> APIResponse:
        """Create a success response."""
        return (self._builder
                .set_status(200)
                .set_data(data)
                .set_message(message)
                .add_metadata({"success": True})
                .build())
    
    def create_error_response(self, code: str, detail: str) -> APIResponse:
        """Create an error response."""
        return (self._builder
                .set_status(400)
                .set_data(None)
                .set_message("Error")
                .add_metadata({"success": False})
                .add_error(code, detail)
                .build())
    
    def create_paginated_response(self, data: List[Any], total: int, page: int,
                                per_page: int = 10) -> APIResponse:
        """Create a paginated response."""
        return (self._builder
                .set_status(200)
                .set_data(data)
                .set_message("Success")
                .add_metadata({"success": True})
                .add_pagination(total, page, per_page)
                .build())


# Usage Example
def main():
    # Create builder and director
    builder = APIResponseBuilder()
    director = ResponseDirector(builder)
    
    # Example 1: Success response
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }
    success_response = director.create_success_response(user_data)
    print("Success Response:", json.dumps(success_response.to_dict(), indent=2))
    
    # Example 2: Error response
    error_response = director.create_error_response(
        code="INVALID_INPUT",
        detail="Email is required"
    )
    print("\nError Response:", json.dumps(error_response.to_dict(), indent=2))
    
    # Example 3: Paginated response with custom builder usage
    users = [
        {"id": i, "name": f"User {i}"} for i in range(1, 6)
    ]
    paginated_response = (builder
                         .set_status(200)
                         .set_data(users)
                         .set_message("Users retrieved successfully")
                         .add_metadata({"success": True})
                         .add_pagination(total=100, page=1, per_page=5)
                         .add_links({
                             "self": "/api/users?page=1",
                             "next": "/api/users?page=2",
                             "last": "/api/users?page=20"
                         })
                         .build())
    print("\nPaginated Response:", json.dumps(paginated_response.to_dict(), indent=2))


if __name__ == "__main__":
    main() 