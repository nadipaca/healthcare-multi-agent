"""
Rate Limiting Middleware for Healthcare Multi-Agent API
Prevents abuse and ensures fair usage
"""
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
import asyncio


class RateLimiter:
    """
    Simple in-memory rate limiter for API requests.
    In production, use Redis or similar distributed cache.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 20,
        requests_per_hour: int = 100,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, List[datetime]] = defaultdict(list)
        self.hour_requests: Dict[str, List[datetime]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def check_rate_limit(self, identifier: str) -> None:
        """
        Check if the request should be rate limited.
        
        Args:
            identifier: Unique identifier (session_id, IP, or user_id)
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        async with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Clean old requests from minute window
            self.minute_requests[identifier] = [
                req_time for req_time in self.minute_requests[identifier]
                if req_time > minute_ago
            ]
            
            # Clean old requests from hour window
            self.hour_requests[identifier] = [
                req_time for req_time in self.hour_requests[identifier]
                if req_time > hour_ago
            ]
            
            # Check minute limit
            if len(self.minute_requests[identifier]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                        "retry_after": 60,
                        "limit_type": "per_minute"
                    }
                )
            
            # Check hour limit
            if len(self.hour_requests[identifier]) >= self.requests_per_hour:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded",
                        "message": f"Maximum {self.requests_per_hour} requests per hour allowed",
                        "retry_after": 3600,
                        "limit_type": "per_hour"
                    }
                )
            
            # Record this request
            self.minute_requests[identifier].append(now)
            self.hour_requests[identifier].append(now)
    
    async def get_remaining_requests(self, identifier: str) -> Dict[str, int]:
        """
        Get remaining requests for an identifier.
        
        Returns:
            Dict with remaining requests per minute and per hour
        """
        async with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            
            # Count recent requests
            minute_count = sum(
                1 for t in self.minute_requests.get(identifier, [])
                if t > minute_ago
            )
            hour_count = sum(
                1 for t in self.hour_requests.get(identifier, [])
                if t > hour_ago
            )
            
            return {
                "remaining_per_minute": max(0, self.requests_per_minute - minute_count),
                "remaining_per_hour": max(0, self.requests_per_hour - hour_count),
                "limit_per_minute": self.requests_per_minute,
                "limit_per_hour": self.requests_per_hour,
            }
    
    async def reset_limits(self, identifier: str) -> None:
        """Reset rate limits for a specific identifier (admin function)"""
        async with self._lock:
            if identifier in self.minute_requests:
                del self.minute_requests[identifier]
            if identifier in self.hour_requests:
                del self.hour_requests[identifier]
    
    async def cleanup_old_entries(self) -> None:
        """
        Periodic cleanup of old entries to prevent memory bloat.
        Should be called by a background task.
        """
        async with self._lock:
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Clean up identifiers with no recent requests
            for identifier in list(self.minute_requests.keys()):
                self.minute_requests[identifier] = [
                    t for t in self.minute_requests[identifier]
                    if t > hour_ago
                ]
                if not self.minute_requests[identifier]:
                    del self.minute_requests[identifier]
            
            for identifier in list(self.hour_requests.keys()):
                self.hour_requests[identifier] = [
                    t for t in self.hour_requests[identifier]
                    if t > hour_ago
                ]
                if not self.hour_requests[identifier]:
                    del self.hour_requests[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=20,  # Adjust based on your needs
    requests_per_hour=100,
)


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware to apply rate limiting to all requests.
    Can be added to FastAPI app.
    """
    # Skip rate limiting for health check and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get identifier (use session_id from request body or IP address)
    identifier = None
    
    # Try to get session_id from request body
    if request.method == "POST":
        try:
            body = await request.body()
            import json
            data = json.loads(body)
            identifier = data.get("session_id")
            # Restore body for next middleware
            async def receive():
                return {"type": "http.request", "body": body}
            request._receive = receive
        except:
            pass
    
    # Fallback to IP address
    if not identifier:
        identifier = request.client.host if request.client else "unknown"
    
    # Check rate limit
    await rate_limiter.check_rate_limit(identifier)
    
    # Add rate limit headers to response
    response = await call_next(request)
    
    # Get remaining requests
    limits = await rate_limiter.get_remaining_requests(identifier)
    response.headers["X-RateLimit-Remaining-Minute"] = str(limits["remaining_per_minute"])
    response.headers["X-RateLimit-Remaining-Hour"] = str(limits["remaining_per_hour"])
    response.headers["X-RateLimit-Limit-Minute"] = str(limits["limit_per_minute"])
    response.headers["X-RateLimit-Limit-Hour"] = str(limits["limit_per_hour"])
    
    return response
