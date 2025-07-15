"""
Decorator Pattern - Backend Implementation

This module demonstrates the Decorator pattern in the context of backend development,
specifically for implementing middleware components that can modify or enhance
API requests and responses.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import time
import logging
import hashlib
import base64


# 1. USE CASES
"""
Backend Use Cases for Decorator Pattern:

1. API Middleware
   - Add authentication/authorization
   - Handle request/response logging
   - Implement rate limiting
   - Add caching layers

2. Data Processing Pipeline
   - Add data validation
   - Implement data transformation
   - Handle data compression
   - Add encryption/decryption

3. Service Enhancement
   - Add performance monitoring
   - Implement retry mechanisms
   - Add circuit breakers
   - Handle error reporting

4. Response Modification
   - Add metadata
   - Implement data formatting
   - Handle data enrichment
   - Add pagination

When to Use:
- When you need to add behavior to objects dynamically
- When you want to avoid class explosion from inheritance
- When you need to stack multiple behaviors

When Not to Use:
- When the behavior is fixed
- When the order of decorators doesn't matter
- When you need to modify the object's interface
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. API Request Handling:
   ```python
   handler = AuthDecorator(
       RateLimitDecorator(
           LoggingDecorator(
               BaseHandler()
           )
       )
   )
   response = handler.handle_request(request)
   ```

2. Data Processing:
   ```python
   processor = ValidationDecorator(
       CompressionDecorator(
           EncryptionDecorator(
               BaseProcessor()
           )
       )
   )
   result = processor.process_data(data)
   ```

3. Service Enhancement:
   ```python
   service = RetryDecorator(
       CircuitBreakerDecorator(
           MonitoringDecorator(
               BaseService()
           )
       )
   )
   result = service.execute()
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class Request:
    """Represents an API request."""
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, str]] = None


@dataclass
class Response:
    """Represents an API response."""
    status_code: int
    body: Dict[str, Any]
    headers: Dict[str, str]


class RequestHandler(ABC):
    """Abstract base class for request handlers."""
    
    @abstractmethod
    def handle_request(self, request: Request) -> Response:
        """Handle an API request."""
        pass


class BaseHandler(RequestHandler):
    """Concrete implementation of request handler."""
    
    def handle_request(self, request: Request) -> Response:
        """Handle the request and return a response."""
        # Simulate processing request
        return Response(
            status_code=200,
            body={"message": "Success", "data": request.body},
            headers={"Content-Type": "application/json"}
        )


class RequestHandlerDecorator(RequestHandler):
    """Base decorator for request handlers."""
    
    def __init__(self, handler: RequestHandler):
        self._handler = handler
    
    def handle_request(self, request: Request) -> Response:
        """Default implementation passes request to wrapped handler."""
        return self._handler.handle_request(request)


class AuthenticationDecorator(RequestHandlerDecorator):
    """Decorator that adds authentication checking."""
    
    def handle_request(self, request: Request) -> Response:
        """Check authentication before handling request."""
        # Check for auth header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                status_code=401,
                body={"error": "Authentication required"},
                headers={"Content-Type": "application/json"}
            )
        
        try:
            # Validate auth token (simplified)
            token = auth_header.split(" ")[1]
            if not self._validate_token(token):
                return Response(
                    status_code=401,
                    body={"error": "Invalid authentication token"},
                    headers={"Content-Type": "application/json"}
                )
            
            # Add user info to request
            if request.body is None:
                request.body = {}
            request.body["user_id"] = "user_123"  # Simplified
            
            return self._handler.handle_request(request)
        
        except Exception as e:
            return Response(
                status_code=500,
                body={"error": f"Authentication error: {str(e)}"},
                headers={"Content-Type": "application/json"}
            )
    
    def _validate_token(self, token: str) -> bool:
        """Validate authentication token (simplified)."""
        return len(token) > 0  # Simplified validation


class RateLimitingDecorator(RequestHandlerDecorator):
    """Decorator that implements rate limiting."""
    
    def __init__(self, handler: RequestHandler, requests_per_minute: int = 60):
        super().__init__(handler)
        self.requests_per_minute = requests_per_minute
        self._request_timestamps: Dict[str, list] = {}
    
    def handle_request(self, request: Request) -> Response:
        """Check rate limit before handling request."""
        # Get client IP (simplified)
        client_ip = request.headers.get("X-Forwarded-For", "unknown")
        
        # Check rate limit
        if not self._check_rate_limit(client_ip):
            return Response(
                status_code=429,
                body={"error": "Rate limit exceeded"},
                headers={"Content-Type": "application/json"}
            )
        
        return self._handler.handle_request(request)
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old timestamps
        if client_ip not in self._request_timestamps:
            self._request_timestamps[client_ip] = []
        self._request_timestamps[client_ip] = [
            ts for ts in self._request_timestamps[client_ip]
            if ts > minute_ago
        ]
        
        # Check rate limit
        if len(self._request_timestamps[client_ip]) >= self.requests_per_minute:
            return False
        
        # Add current timestamp
        self._request_timestamps[client_ip].append(now)
        return True


class LoggingDecorator(RequestHandlerDecorator):
    """Decorator that adds request/response logging."""
    
    def __init__(self, handler: RequestHandler):
        super().__init__(handler)
        self.logger = logging.getLogger(__name__)
    
    def handle_request(self, request: Request) -> Response:
        """Log request and response."""
        start_time = time.time()
        
        # Log request
        self.logger.info(
            "Request: %s %s",
            request.method,
            request.path,
            extra={
                "headers": request.headers,
                "body": request.body,
                "query_params": request.query_params
            }
        )
        
        try:
            # Handle request
            response = self._handler.handle_request(request)
            
            # Log response
            self.logger.info(
                "Response: %d %s",
                response.status_code,
                "Success" if response.status_code < 400 else "Error",
                extra={
                    "duration": time.time() - start_time,
                    "headers": response.headers,
                    "body": response.body
                }
            )
            
            return response
        
        except Exception as e:
            # Log error
            self.logger.error(
                "Error handling request: %s",
                str(e),
                exc_info=True,
                extra={
                    "duration": time.time() - start_time
                }
            )
            raise


class CachingDecorator(RequestHandlerDecorator):
    """Decorator that adds response caching."""
    
    def __init__(self, handler: RequestHandler, ttl_seconds: int = 300):
        super().__init__(handler)
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[float, Response]] = {}
    
    def handle_request(self, request: Request) -> Response:
        """Check cache before handling request."""
        # Only cache GET requests
        if request.method != "GET":
            return self._handler.handle_request(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            timestamp, response = cached
            if time.time() - timestamp < self.ttl_seconds:
                # Add cache header
                response.headers["X-Cache"] = "HIT"
                return response
        
        # Handle request
        response = self._handler.handle_request(request)
        
        # Cache response
        if response.status_code == 200:
            self._cache[cache_key] = (time.time(), response)
            response.headers["X-Cache"] = "MISS"
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        # Create string with method, path, and sorted query params
        key_parts = [request.method, request.path]
        
        if request.query_params:
            sorted_params = sorted(
                f"{k}={v}"
                for k, v in request.query_params.items()
            )
            key_parts.extend(sorted_params)
        
        # Generate hash
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


# Usage Example
def main():
    # Create a handler with multiple decorators
    handler = CachingDecorator(
        LoggingDecorator(
            RateLimitingDecorator(
                AuthenticationDecorator(
                    BaseHandler()
                ),
                requests_per_minute=2  # Low limit for demonstration
            )
        )
    )
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Test requests
        for i in range(3):
            # Create request
            request = Request(
                method="GET",
                path="/api/data",
                headers={
                    "Authorization": "Bearer test_token",
                    "X-Forwarded-For": "127.0.0.1",
                    "Content-Type": "application/json"
                },
                query_params={"id": str(i)},
                body={"test": "data"}
            )
            
            # Handle request
            print(f"\nRequest {i + 1}:")
            response = handler.handle_request(request)
            
            # Print response
            print("Status:", response.status_code)
            print("Headers:", json.dumps(response.headers, indent=2))
            print("Body:", json.dumps(response.body, indent=2))
            
            # Small delay between requests
            time.sleep(0.1)
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 