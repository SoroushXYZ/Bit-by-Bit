#!/usr/bin/env python3
"""
Minimal FastAPI app to echo caller IP information.
- Shows request.client.host (socket source IP)
- Shows common proxy headers (CF-Connecting-IP, X-Forwarded-For, X-Real-IP)
- Optionally trusts Cloudflare headers only if immediate peer is in CF ranges (toggle via TRUST_CLOUDFLARE env)
Run:
  uvicorn ip_echo_app:app --host 0.0.0.0 --port 8080 --proxy-headers
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

app = FastAPI(title="IP Echo App", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cloudflare IP ranges (can be updated from https://www.cloudflare.com/ips/)
CF_IPV4 = [
    "173.245.48.0/20","103.21.244.0/22","103.22.200.0/22","103.31.4.0/22",
    "141.101.64.0/18","108.162.192.0/18","190.93.240.0/20","188.114.96.0/20",
    "197.234.240.0/22","198.41.128.0/17","162.158.0.0/15","104.16.0.0/13",
    "104.24.0.0/14","172.64.0.0/13","131.0.72.0/22"
]
CF_IPV6 = [
    "2400:cb00::/32","2606:4700::/32","2803:f800::/32","2405:b500::/32",
    "2405:8100::/32","2a06:98c0::/29","2c0f:f248::/32"
]

TRUST_CLOUDFLARE = os.getenv("TRUST_CLOUDFLARE", "false").lower() == "true"

# Simple CIDR match helper
from ipaddress import ip_address, ip_network

def ip_in_any_cidr(ip: str, cidrs) -> bool:
    try:
        ip_obj = ip_address(ip)
        for c in cidrs:
            if ip_obj in ip_network(c):
                return True
    except Exception:
        return False
    return False

@app.get("/")
async def root():
    return {"message": "IP Echo App running"}

@app.get("/ip")
async def ip_info(request: Request) -> Dict[str, Any]:
    peer_ip = request.client.host if request.client else None
    headers = request.headers

    cf_connecting_ip = headers.get("cf-connecting-ip")
    x_forwarded_for = headers.get("x-forwarded-for")
    x_real_ip = headers.get("x-real-ip")
    real_ip = None
    trusted = False

    # Decide which IP to report as real client IP
    if TRUST_CLOUDFLARE and peer_ip and (ip_in_any_cidr(peer_ip, CF_IPV4) or ip_in_any_cidr(peer_ip, CF_IPV6)):
        # Trust Cloudflare headers only if the immediate peer is Cloudflare
        if cf_connecting_ip:
            real_ip = cf_connecting_ip
            trusted = True
        elif x_forwarded_for:
            real_ip = x_forwarded_for.split(',')[0].strip()
            trusted = True
        elif x_real_ip:
            real_ip = x_real_ip
            trusted = True
    else:
        # Either not trusting CF, or peer isn't CF → use socket IP or XFF best-effort
        if x_forwarded_for:
            real_ip = x_forwarded_for.split(',')[0].strip()
        elif x_real_ip:
            real_ip = x_real_ip
        else:
            real_ip = peer_ip

    return {
        "peer_ip": peer_ip,                   # immediate connection IP (likely proxy/CDN)
        "real_ip": real_ip,                   # best-guess client IP
        "trusted_cloudflare": TRUST_CLOUDFLARE,
        "trusted_source_is_cf": peer_ip and (ip_in_any_cidr(peer_ip, CF_IPV4) or ip_in_any_cidr(peer_ip, CF_IPV6)),
        "headers": {
            "cf-connecting-ip": cf_connecting_ip,
            "x-forwarded-for": x_forwarded_for,
            "x-real-ip": x_real_ip,
            "user-agent": headers.get("user-agent"),
            "via": headers.get("via"),
            "forwarded": headers.get("forwarded"),
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ip_echo_app:app", host="0.0.0.0", port=8080, reload=True, proxy_headers=True)
