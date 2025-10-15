from fastapi import FastAPI, Request
import httpx

app = FastAPI()


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


@app.get("/check_ip")
async def check_ip(request: Request):
    """API endpoint to check if client IP is mobile."""
    # Get client IP (from headers or remote address)
    ip = (
        request.headers.get("x-forwarded-for")
        or request.client.host
        or "127.0.0.1"
    )
    ip = ip.split(",")[0].strip()

    is_mobile = await is_mobile_ip(ip)
    return {
        "ip": ip,
        "is_mobile": is_mobile,
    }
