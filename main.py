from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="IP Checker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def is_mobile_ip(ip: str) -> bool:
    """Check if the given IP is mobile, proxy, or hosting."""
    fields = "status,message,mobile,proxy,hosting,query"
    url = f"http://ip-api.com/json/{ip}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url, params={"fields": fields})
            data = response.json()
    except Exception:
        return False  # connection or timeout error

    if data.get("status") != "success":
        return False

    if data.get("mobile"):
        return True
    if data.get("proxy") or data.get("hosting"):
        return False

    return False

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "IP Checker API",
        "endpoints": {
            "/check_ip": "Check if client IP is mobile",
            "/docs": "API documentation"
        }
    }

@app.get("/check_ip")
async def check_ip(request: Request):
    """API endpoint to check if client IP is mobile."""
    # Get client IP (from headers or remote address)
    ip = (
        request.headers.get("x-forwarded-for")
        or request.headers.get("x-real-ip")
        or request.client.host
        or "127.0.0.1"
    )
    ip = ip.split(",")[0].strip()

    is_mobile = await is_mobile_ip(ip)
    return {
        "ip": ip,
        "is_mobile": is_mobile,
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy"}

# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)