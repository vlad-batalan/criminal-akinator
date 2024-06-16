from __future__ import annotations

from pydantic import BaseModel

class Question(BaseModel):
    name: str
    answer: str | None = None


class GuessInput(BaseModel):
    questions: list[Question]
    max_depth: int = 20


class GuessOutput(BaseModel):
    question: str | None = None
    values: list[str] | None = None
    guess: str | None = None
