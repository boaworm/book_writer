from pydantic import BaseModel, model_validator


class BookLLMOverrides(BaseModel):
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    top_k: int | None = None
    min_p: float | None = None


class Universe(BaseModel):
    name: str
    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def coerce_string(cls, v: object) -> object:
        if isinstance(v, str):
            return {"name": v}
        return v


class BookConfig(BaseModel):
    category: str = "novel"
    writing_style: str | None = None
    universe: Universe | None = None
    model: str | None = None
    base_url: str | None = None
    llm: BookLLMOverrides = BookLLMOverrides()
