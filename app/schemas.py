from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Literal

class LinkAnalysisRequest(BaseModel):
    url: HttpUrl

class Competitor(BaseModel):
    name: str
    overview: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses_or_gaps: list[str] = Field(default_factory=list)
    evidence_status: Literal["verified", "ai_suggested_unverified"] = "ai_suggested_unverified"
    source_urls: list[str] = Field(default_factory=list)

class CompetitorAnalysis(BaseModel):
    brand_overview: str
    business_category: str
    main_products_services: list[str]
    competitors: list[Competitor] = Field(default_factory=list)
    your_brand_strengths: list[str] = Field(default_factory=list)
    competitive_advantages: list[str] = Field(default_factory=list)
    positioning_opportunities: list[str] = Field(default_factory=list)

class SearchQuery(BaseModel):
    query: str
    platforms: list[Literal["Google", "Facebook", "Instagram", "LinkedIn", "X (Twitter)"]]
    intent: str
    business_relevance: str
    target_audience: str

class SEOImprovements(BaseModel):
    primary_keyword: str
    secondary_keywords: list[str] = Field(default_factory=list)
    long_tail_keywords: list[str] = Field(default_factory=list)
    business_keywords: list[str] = Field(default_factory=list)
    recommended_title: str
    title_primary_keyword: str
    title_structure: str
    meta_description: str
    supporting_content: list[str] = Field(default_factory=list)

class Service(BaseModel):
    service_name: str
    description: str
    target_industry: str
    target_customer: str
    main_benefit: str
    identification: Literal["found_on_website", "inferred_recommendation"]

class TargetAudience(BaseModel):
    primary_audience: list[str] = Field(default_factory=list)
    secondary_audience: list[str] = Field(default_factory=list)
    industries: list[str] = Field(default_factory=list)
    business_types: list[str] = Field(default_factory=list)
    customer_profiles: list[str] = Field(default_factory=list)
    geographical_focus: list[str] = Field(default_factory=list)
    customer_needs: list[str] = Field(default_factory=list)
    potential_interests: list[str] = Field(default_factory=list)
    recommended_marketing_segments: list[str] = Field(default_factory=list)

class AnalysisPayload(BaseModel):
    competitor_analysis: CompetitorAnalysis
    target_search_queries: list[SearchQuery] = Field(min_length=5, max_length=5)
    seo_improvements: SEOImprovements
    top_services: list[Service] = Field(min_length=5, max_length=5)
    target_audience: TargetAudience

class Brand(BaseModel):
    name: str
    category: str
    summary: str

class LinkAnalysisResponse(BaseModel):
    success: bool = True
    website: str
    brand: Brand
    analysis: AnalysisPayload
    extraction: dict
    llm: dict
