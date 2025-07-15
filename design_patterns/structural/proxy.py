"""
Proxy Pattern - Backend Implementation

This module demonstrates the Proxy pattern in the context of backend development,
specifically for implementing API gateways, access control, and service proxies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time
import logging
import hashlib
import base64
import jwt


# 1. USE CASES
"""
Backend Use Cases for Proxy Pattern:

1. API Gateway
   - Route requests to services
   - Handle authentication/authorization
   - Implement rate limiting
   - Manage request/response transformation

2. Service Access Control
   - Control access to sensitive services
   - Implement role-based access
   - Manage service permissions
   - Log service access

3. Caching Proxy
   - Cache service responses
   - Manage cache invalidation
   - Handle cache updates
   - Optimize performance

4. Load Balancing
   - Distribute requests across services
   - Handle service health checks
   - Manage service discovery
   - Implement failover

When to Use:
- When you need to control access to a service
- When you want to add functionality without changing the service
- When you need to manage service interactions

When Not to Use:
- When direct service access is required
- When proxy adds unnecessary complexity
- When performance overhead is unacceptable
"""


# 2. EXAMPLES
"""
Example Scenarios:

1. API Gateway:
   ```python
   gateway = APIGatewayProxy(service)
   response = gateway.handle_request(request)
   # Handles authentication, routing, and transformation
   ```

2. Service Access:
   ```python
   protected_service = AccessControlProxy(service)
   result = protected_service.execute(request)
   # Checks permissions before execution
   ```

3. Caching:
   ```python
   cached_service = CachingProxy(service)
   data = cached_service.get_data(key)
   # Returns cached data if available
   ```
"""


# 3. IMPLEMENTATION

@dataclass
class Request:
    """API request details."""
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, str]] = None


@dataclass
class Response:
    """API response details."""
    status_code: int
    body: Dict[str, Any]
    headers: Dict[str, str]


class Service(ABC):
    """Abstract base class for services."""
    
    @abstractmethod
    def handle_request(self, request: Request) -> Response:
        """Handle an API request."""
        pass


class UserService(Service):
    """Concrete service for user management."""
    
    def handle_request(self, request: Request) -> Response:
        """Handle user-related requests."""
        if request.method == "GET" and request.path == "/users":
            return Response(
                status_code=200,
                body={"users": [
                    {"id": 1, "name": "John Doe"},
                    {"id": 2, "name": "Jane Smith"}
                ]},
                headers={"Content-Type": "application/json"}
            )
        elif request.method == "POST" and request.path == "/users":
            return Response(
                status_code=201,
                body={"message": "User created", "user": request.body},
                headers={"Content-Type": "application/json"}
            )
        else:
            return Response(
                status_code=404,
                body={"error": "Not found"},
                headers={"Content-Type": "application/json"}
            )


class ServiceProxy(Service):
    """Base proxy class for services."""
    
    def __init__(self, service: Service):
        self._service = service


class AuthenticationProxy(ServiceProxy):
    """Proxy that handles authentication."""
    
    def __init__(self, service: Service, secret_key: str):
        super().__init__(service)
        self._secret_key = secret_key
    
    def handle_request(self, request: Request) -> Response:
        """Authenticate request before handling."""
        # Check for auth token
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return Response(
                status_code=401,
                body={"error": "Authentication required"},
                headers={"Content-Type": "application/json"}
            )
        
        try:
            # Validate JWT token
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, self._secret_key, algorithms=["HS256"])
            
            # Add user info to request
            if request.body is None:
                request.body = {}
            request.body["user_id"] = payload["sub"]
            
            # Handle request
            return self._service.handle_request(request)
        
        except jwt.InvalidTokenError:
            return Response(
                status_code=401,
                body={"error": "Invalid token"},
                headers={"Content-Type": "application/json"}
            )
        except Exception as e:
            return Response(
                status_code=500,
                body={"error": str(e)},
                headers={"Content-Type": "application/json"}
            )


class RateLimitingProxy(ServiceProxy):
    """Proxy that implements rate limiting."""
    
    def __init__(self, service: Service, requests_per_minute: int = 60):
        super().__init__(service)
        self._requests_per_minute = requests_per_minute
        self._request_timestamps: Dict[str, List[float]] = {}
    
    def handle_request(self, request: Request) -> Response:
        """Check rate limit before handling request."""
        client_ip = request.headers.get("X-Forwarded-For", "unknown")
        
        if not self._check_rate_limit(client_ip):
            return Response(
                status_code=429,
                body={"error": "Rate limit exceeded"},
                headers={"Content-Type": "application/json"}
            )
        
        return self._service.handle_request(request)
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded rate limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Initialize or clean old timestamps
        if client_ip not in self._request_timestamps:
            self._request_timestamps[client_ip] = []
        
        # Remove old timestamps
        self._request_timestamps[client_ip] = [
            ts for ts in self._request_timestamps[client_ip]
            if ts > minute_ago
        ]
        
        # Check rate limit
        if len(self._request_timestamps[client_ip]) >= self._requests_per_minute:
            return False
        
        # Add current timestamp
        self._request_timestamps[client_ip].append(now)
        return True


class CachingProxy(ServiceProxy):
    """Proxy that implements response caching."""
    
    def __init__(self, service: Service, ttl_seconds: int = 300):
        super().__init__(service)
        self._ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[float, Response]] = {}
    
    def handle_request(self, request: Request) -> Response:
        """Check cache before handling request."""
        # Only cache GET requests
        if request.method != "GET":
            return self._service.handle_request(request)
        
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        cached = self._cache.get(cache_key)
        if cached:
            timestamp, response = cached
            if time.time() - timestamp < self._ttl_seconds:
                response.headers["X-Cache"] = "HIT"
                return response
        
        # Handle request
        response = self._service.handle_request(request)
        
        # Cache successful responses
        if response.status_code == 200:
            self._cache[cache_key] = (time.time(), response)
            response.headers["X-Cache"] = "MISS"
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        key_parts = [request.method, request.path]
        
        if request.query_params:
            sorted_params = sorted(
                f"{k}={v}"
                for k, v in request.query_params.items()
            )
            key_parts.extend(sorted_params)
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


class LoggingProxy(ServiceProxy):
    """Proxy that implements request/response logging."""
    
    def __init__(self, service: Service):
        super().__init__(service)
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
            response = self._service.handle_request(request)
            
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


# Usage Example
def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create service with multiple proxies
    service = UserService()
    proxy = CachingProxy(
        LoggingProxy(
            RateLimitingProxy(
                AuthenticationProxy(
                    service,
                    secret_key="your-secret-key"
                ),
                requests_per_minute=2
            )
        )
    )
    
    try:
        # Create JWT token for testing
        token = jwt.encode(
            {"sub": "user_123", "exp": datetime.utcnow() + timedelta(hours=1)},
            "your-secret-key",
            algorithm="HS256"
        )
        
        # Test requests
        for i in range(3):
            # Create request
            request = Request(
                method="GET",
                path="/users",
                headers={
                    "Authorization": f"Bearer {token}",
                    "X-Forwarded-For": "127.0.0.1",
                    "Content-Type": "application/json"
                }
            )
            
            # Handle request
            print(f"\nRequest {i + 1}:")
            response = proxy.handle_request(request)
            
            # Print response
            print("Status:", response.status_code)
            print("Headers:", json.dumps(response.headers, indent=2))
            print("Body:", json.dumps(response.body, indent=2))
            
            # Small delay between requests
            time.sleep(0.1)
        
        # Test invalid token
        print("\nTesting invalid token:")
        request = Request(
            method="GET",
            path="/users",
            headers={
                "Authorization": "Bearer invalid-token",
                "X-Forwarded-For": "127.0.0.1",
                "Content-Type": "application/json"
            }
        )
        response = proxy.handle_request(request)
        print("Status:", response.status_code)
        print("Body:", json.dumps(response.body, indent=2))
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 