from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.schemas import LinkAnalysisRequest, LinkAnalysisResponse
from app.services.analysis_service import run_analysis
from app.utils.validators import validate_public_url

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0",
              description="Extracts website content and generates structured business and SEO insights.")

@app.get("/health")
async def health():
    return {"status": "ok", "provider": settings.llm_provider}

@app.post("/link-analysis", response_model=LinkAnalysisResponse)
async def link_analysis(payload: LinkAnalysisRequest):
    url = str(payload.url)
    validate_public_url(url)
    try:
        return await run_analysis(url)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=f"LLM returned invalid structured output: {exc}")
    except Exception as exc:
        # Do not expose provider credentials or raw upstream errors to API clients.
        raise HTTPException(status_code=502, detail="Website analysis failed. Check provider configuration and try again.") from exc

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content={"success": False, "error": exc.detail})
