"""ReleaseScope HTTP API and dashboard."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from analysis_core import compare
from build_demo import build

app = FastAPI(title="ReleaseScope", version="1.0.0")
root = Path(__file__).parent


class Observation(BaseModel):
    latency_ms: float = Field(ge=0, allow_inf_nan=False)
    status: int = Field(ge=100, le=599)


class Comparison(BaseModel):
    before: list[Observation] = Field(min_length=1, max_length=50000)
    after: list[Observation] = Field(min_length=1, max_length=50000)


@app.post("/api/compare")
def compare_release(payload: Comparison):
    def rows(window):
        return [(r.latency_ms, r.status) for r in window]
    return compare(rows(payload.before), rows(payload.after))


@app.get("/demo.json")
def demo():
    return build()


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(root / "index.html")
