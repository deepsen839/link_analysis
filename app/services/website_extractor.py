import ipaddress, socket
from urllib.parse import urljoin, urlsplit
import httpx
from bs4 import BeautifulSoup
from fastapi import HTTPException
from app.utils.validators import validate_public_url

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; LinkAnalysisBot/1.0; +https://example.org/bot)"}

def _check_host_again(url: str):
    # Re-check every redirect target. For hardened production deployments, also
    # enforce public egress at the network layer to mitigate DNS rebinding.
    validate_public_url(url)

async def fetch_website(url: str, timeout: float, max_bytes: int) -> dict:
    current = str(url)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, headers=HEADERS) as client:
        for _ in range(4):
            _check_host_again(current)
            try:
                async with client.stream("GET", current) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        location = response.headers.get("location")
                        if not location:
                            raise HTTPException(502, "Website returned an invalid redirect.")
                        current = urljoin(current, location)
                        continue
                    if response.status_code >= 400:
                        raise HTTPException(502, f"Website returned HTTP {response.status_code}.")
                    content_type = response.headers.get("content-type", "")
                    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
                        raise HTTPException(422, "The URL did not return an HTML page.")
                    chunks, total = [], 0
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if total > max_bytes:
                            raise HTTPException(413, "Website HTML exceeds the configured size limit.")
                        chunks.append(chunk)
                    raw = b"".join(chunks)
                break
            except httpx.TimeoutException:
                raise HTTPException(504, "Timed out while fetching the website.")
            except httpx.RequestError:
                raise HTTPException(502, "Could not connect to the website.")
        else:
            raise HTTPException(502, "Too many redirects.")

    soup = BeautifulSoup(raw, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    og_site = soup.find("meta", property="og:site_name")
    brand_name = og_site.get("content", "").strip() if og_site else ""
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = description_tag.get("content", "").strip() if description_tag else ""
    canonical_tag = soup.find("link", rel="canonical")
    canonical = canonical_tag.get("href") if canonical_tag else None
    headings = {f"h{i}": [x.get_text(" ", strip=True) for x in soup.find_all(f"h{i}")][:15] for i in range(1, 4)}
    for tag in soup(["script", "style", "noscript", "svg", "nav", "footer", "header", "form"]):
        tag.decompose()
    text = " ".join(soup.stripped_strings)
    text = " ".join(text.split())
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(current, a["href"])
        if urlsplit(href).scheme in {"http", "https"}:
            label = a.get_text(" ", strip=True)
            if label:
                links.append({"text": label[:120], "url": href})
    return {
        "final_url": current, "title": title, "brand_name": brand_name, "meta_description": description,
        "canonical_url": canonical, "headings": headings,
        "text": text[:100000], "links": links[:60],
        "html_bytes": len(raw), "text_chars": len(text)
    }
