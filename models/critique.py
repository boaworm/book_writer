from typing import Literal

from pydantic import BaseModel


class CritiqueIssue(BaseModel):
    area: Literal["Premise", "Characters", "Structure", "Pacing", "Scenes", "Category"]
    severity: Literal["critical", "warning", "suggestion"]
    issue: str
    recommendation: str


class CritiqueResult(BaseModel):
    overall_assessment: str
    score: int  # 1–10
    issues: list[CritiqueIssue]
