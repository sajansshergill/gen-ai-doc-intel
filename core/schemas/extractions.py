"""
Structured extraction schemas for different document types.
These enforce schema-validated JSON outputs.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence citation."""
    doc_id: str
    page: int
    chunk_id: str
    score: Optional[float] = None
    snippet: Optional[str] = None


class RiskFactor(BaseModel):
    """Risk factor extraction."""
    risk: str = Field(..., description="Description of the risk")
    category: Optional[str] = Field(None, description="Risk category (e.g., financial, operational)")
    severity: Optional[str] = Field(None, description="Severity level")
    evidence: List[Evidence] = Field(default_factory=list, description="Supporting evidence")


class RiskSummaryV1(BaseModel):
    """Risk summary schema - for financial/risk documents."""
    risks: List[RiskFactor] = Field(default_factory=list)
    total_risks: int = 0
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)


class Entity(BaseModel):
    """Entity extraction."""
    name: str
    type: str  # "person", "organization", "date", "amount", "location", etc.
    value: str
    page: Optional[int] = None
    confidence: Optional[float] = None
    evidence: List[Evidence] = Field(default_factory=list)


class KPIMetric(BaseModel):
    """KPI/metric extraction."""
    metric_name: str
    value: str
    unit: Optional[str] = None
    period: Optional[str] = None
    page: Optional[int] = None
    evidence: List[Evidence] = Field(default_factory=list)


class FinancialSummary(BaseModel):
    """Financial summary extraction."""
    kpis: List[KPIMetric] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)


class DocumentSummary(BaseModel):
    """General document summary."""
    summary: str
    key_points: List[str] = Field(default_factory=list)
    entities: List[Entity] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
