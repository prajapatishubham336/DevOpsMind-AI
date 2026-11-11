import time
import socket
import ipaddress
from urllib.parse import urlparse

import httpx


def validate_public_url(url):
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid HTTP or HTTPS URL.")

    hostname = parsed.hostname.lower()

    if hostname == "localhost":
        raise ValueError("Localhost URLs are not allowed.")

    try:
        addresses = socket.getaddrinfo(hostname, None)
        for address in addresses:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                raise ValueError("Private or internal network URLs are not allowed.")
    except socket.gaierror:
        raise ValueError("The website hostname could not be resolved.")

    return url


async def check_website(url):
    validate_public_url(url)
    start_time = time.perf_counter()

    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=False
        ) as client:
            response = await client.get(url)

        elapsed = round((time.perf_counter() - start_time) * 1000, 2)

        status = (
            "healthy"
            if 200 <= response.status_code < 400
            else "error"
        )

        return {
            "status": status,
            "status_code": response.status_code,
            "response_time_ms": elapsed,
            "message": "Website responded successfully."
            if status == "healthy"
            else "Website returned an HTTP error."
        }

    except httpx.TimeoutException:
        return {
            "status": "unreachable",
            "status_code": None,
            "response_time_ms": None,
            "message": "Website request timed out."
        }

    except httpx.RequestError as error:
        return {
            "status": "unreachable",
            "status_code": None,
            "response_time_ms": None,
            "message": f"Website connection failed: {str(error)}"
        }