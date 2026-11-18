import hashlib, json, time
from app.services.website_extractor import fetch_website
from app.services.llm_service import analyze_with_llm
from app.config import get_settings
from app.schemas import Brand, LinkAnalysisResponse

_CACHE: dict[str, tuple[float, dict]] = {}

async def run_analysis(url: str) -> LinkAnalysisResponse:
    cfg = get_settings()
    key = hashlib.sha256(url.encode()).hexdigest()
    now = time.time()
    cached = _CACHE.get(key)
    if cached and now - cached[0] < cfg.cache_ttl_seconds:
        data = cached[1].copy()
        data["extraction"]["cache_hit"] = True
        return LinkAnalysisResponse.model_validate(data)

    site = await fetch_website(url, cfg.request_timeout_seconds, cfg.max_html_bytes)
    analysis, llm_meta = await analyze_with_llm(site)
    brand_name = site.get("brand_name") or (site["title"].split("|")[0].split(" - ")[0].strip() if site["title"] else url)
    summary = site["meta_description"] or site["text"][:280]
    category = analysis.competitor_analysis.business_category
    response = LinkAnalysisResponse(
        website=site["final_url"],
        brand=Brand(name=brand_name[:120], category=category, summary=summary[:500]),
        analysis=analysis,
        extraction={"title": site["title"], "meta_description": site["meta_description"],
                    "headings": site["headings"], "html_bytes": site["html_bytes"],
                    "text_chars": site["text_chars"], "cache_hit": False},
        llm=llm_meta,
    )
    _CACHE[key] = (now, response.model_dump(mode="json"))
    # Keep this simple in-memory cache bounded.
    if len(_CACHE) > 500:
        oldest = sorted(_CACHE.items(), key=lambda item: item[1][0])[:100]
        for old_key, _ in oldest:
            _CACHE.pop(old_key, None)
    return response
