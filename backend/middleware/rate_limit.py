from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import os

# Rate limiting configuration
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
WINDOW_SIZE = 60  # 1 minute in seconds

# In-memory storage for rate limiting
# In production, use Redis or similar
request_counts = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    # Get client IP
    client_ip = request.client.host
    
    # Get current timestamp
    current_time = time.time()
    
    # Clean up old requests
    request_counts[client_ip] = [
        timestamp for timestamp in request_counts[client_ip]
        if current_time - timestamp < WINDOW_SIZE
    ]
    
    # Check if rate limit exceeded
    if len(request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Too many requests. Please try again later.",
                "retry_after": int(WINDOW_SIZE - (current_time - request_counts[client_ip][0]))
            }
        )
    
    # Add current request timestamp
    request_counts[client_ip].append(current_time)
    
    # Process the request
    response = await call_next(request)
    return response 